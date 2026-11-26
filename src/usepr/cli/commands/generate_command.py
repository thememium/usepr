"""GenerateCommand - CLI command."""

from __future__ import annotations

import os
from typing import Annotated

import pyperclip
from usecli import (
    BaseCommand,
    Menu,
    Option,
    Panel,
    Prompt,
    Spinner,
    Syntax,
    console,
    theme,
)

from usepr.configs.dspy import configure_dspy
from usepr.services.pr_summary_service import (
    gather_commits,
    generate_summary,
    generate_title,
    get_templates,
)
from usepr.utils.github import PrTemplate

OTHER_BRANCH = "Other... (type a branch name)"


class GenerateCommand(BaseCommand):
    def signature(self) -> str:
        return "generate"

    def description(self) -> str:
        return "Description for generate command"

    def aliases(self) -> list[str]:
        return ["gen"]

    def _prompt_for_template(self, templates: list[PrTemplate]) -> PrTemplate | None:
        """Prompt the user to select a PR template, or skip."""
        if not templates:
            return None

        if len(templates) == 1:
            t = templates[0]
            label = t.name or os.path.basename(t.path)
            use = (
                (
                    Prompt.ask(
                        f"\n[bold {theme.ACCENT}]Found PR template:[/bold {theme.ACCENT}] {label} — use it?",
                        default="y",
                        choices=["y", "n"],
                        show_choices=False,
                    )
                    or ""
                )
                .lower()
                .strip()
            )
            return t if use == "y" else None

        console.print(
            f"\n[bold {theme.ACCENT}]Found {len(templates)} PR templates:[/bold {theme.ACCENT}]"
        )
        for i, t in enumerate(templates, 1):
            label = t.name or os.path.basename(t.path)
            console.print(f"  {i}. {label} [dim]({t.path})[/dim]")

        console.print("  0. [dim]Skip template[/dim]")

        choice = Prompt.ask(
            "Select a template number",
            default="0",
        )
        try:
            idx = int(choice) if choice else 0
        except ValueError:
            return None
        if idx == 0 or idx > len(templates):
            return None
        return templates[idx - 1]

    def _offer_clipboard(self, content: str, label: str) -> None:
        """Ask whether to copy content, then copy it and report the result."""
        copy_to_clipboard = (
            (
                Prompt.ask(
                    f"\n[bold {theme.WARNING}]Copy {label.lower()} to clipboard?[/bold {theme.WARNING}]",
                    default="y",
                    choices=["y", "n"],
                )
                or ""
            )
            .lower()
            .strip()
        )
        if copy_to_clipboard not in ["y", "yes"]:
            return
        try:
            pyperclip.copy(content)
            console.print(
                f"[bold {theme.SECONDARY}]✓ {label} copied to clipboard![/bold {theme.SECONDARY}]"
            )
        except (pyperclip.PyperclipException, OSError) as e:
            console.print(
                f"[bold {theme.ERROR}]✗ Failed to copy {label.lower()} to clipboard: {e}[/bold {theme.ERROR}]"
            )

    def handle(
        self,
        model: Annotated[
            str | None,
            Option("-m", "--model", help="Override the default LLM model."),
        ] = None,
    ) -> None:

        repo = os.path.abspath(".")

        from usepr.utils.git import (
            ensure_git_repo,
            get_branch_selection_options,
            get_current_branch,
            get_default_branch,
        )

        ensure_git_repo(repo)
        configure_dspy(model)

        console.clear()
        console.print(f"[bold {theme.PRIMARY}]Pull Request Summary Generator")

        console.line()

        default_branch = get_default_branch(repo).strip()
        options = get_branch_selection_options(repo, default_branch) + [OTHER_BRANCH]
        selected = Menu.select(
            options,
            title=f"Base branch to diff against (default: {default_branch})",
        )

        if selected is None:
            console.print(
                f"[bold {theme.WARNING}]No base branch selected; aborting.[/bold {theme.WARNING}]"
            )
            return

        if selected == OTHER_BRANCH:
            base_branch = (
                Prompt.ask(
                    f"[bold {theme.ACCENT}]Enter base branch to diff against[/bold {theme.ACCENT}]",
                    default=default_branch,
                )
                or ""
            ).strip()
        else:
            base_branch = selected

        console.print(
            f"[bold {theme.SUCCESS}]Base branch:[/bold {theme.SUCCESS}] "
            f"[bold {theme.ACCENT}]{base_branch}[/bold {theme.ACCENT}]"
        )

        commit_ctx = gather_commits(repo, base_branch)

        if not commit_ctx.commits:
            console.print(
                "[red]No commits found between the specified tags or branches."
            )
            return

        console.line()

        related_issues = Prompt.ask(
            f"[bold {theme.ACCENT}]List any related issues or tasks "
            f"(comma-separated), or leave blank if none[/bold {theme.ACCENT}]",
            default="",
            show_default=False,
        )

        templates = get_templates(repo)
        selected_template = self._prompt_for_template(templates)
        template_content = selected_template.content if selected_template else None

        branch_name = get_current_branch(repo) or None

        with Spinner("Generating PR title..."):
            title_result = generate_title(
                commits=commit_ctx.commits,
                related_issues=related_issues,
                branch_name=branch_name,
            )

        console.print()
        console.print(
            Panel(
                title_result.title,
                title="Pull Request Title",
                border_style=theme.SECONDARY,
                title_align="left",
            )
        )
        self._offer_clipboard(title_result.title, "Title")

        console.line()

        with Spinner("Generating PR summary..."):
            result = generate_summary(
                commits=commit_ctx.commits,
                related_issues=related_issues,
                template=template_content,
            )

        console.print()

        summary_md = Syntax(
            result.summary,
            "markdown",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        console.print(
            Panel(
                summary_md,
                title="Pull Request Summary",
                border_style=theme.SECONDARY,
                title_align="left",
            )
        )

        self._offer_clipboard(result.summary, "Summary")
