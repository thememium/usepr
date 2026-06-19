"""GenerateCommand - CLI command."""

from __future__ import annotations

import os
from typing import Annotated, Optional

import pyperclip
import typer
from rich.panel import Panel
from rich.syntax import Syntax
from usecli import BaseCommand, Prompt, console, theme

from usepr.configs.dspy import configure_dspy
from usepr.services.pr_summary_service import (
    gather_commits,
    generate_summary,
    get_templates,
)
from usepr.utils.github import PrTemplate


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

    def handle(
        self,
        model: Annotated[
            Optional[str],
            typer.Option("-m", "--model", help="Override the default LLM model."),
        ] = None,
    ) -> None:

        configure_dspy(model)

        repo = os.path.abspath(".")

        console.clear()
        console.print(f"[bold {theme.PRIMARY}]Pull Request Summary Generator")

        from usepr.utils.git import get_default_branch

        default_branch = get_default_branch(repo).strip()
        base_branch = (
            Prompt.ask(
                f"\n[bold {theme.ACCENT}]Base branch to diff against[/bold {theme.ACCENT}] [dim](default: {default_branch})[/dim]",
                default="",
            )
            or ""
        ).strip()

        if not base_branch:
            base_branch = default_branch

        commit_ctx = gather_commits(repo, base_branch)

        if not commit_ctx.commits:
            console.print(
                "[red]No commits found between the specified tags or branches."
            )
            return

        # proceed = Prompt.ask(
        #     "Do you want to proceed with generating the summary?",
        #     default="y",
        #     choices=["y", "n"],
        #     show_choices=False,
        # )
        # if proceed and proceed.lower() != "y":
        #     console.print("Aborting summary generation.")
        #     return

        related_issues = Prompt.ask(
            "List any related issues or tasks (comma-separated), or leave blank if none:",
            default="",
        )

        templates = get_templates(repo)
        selected_template = self._prompt_for_template(templates)
        template_content = selected_template.content if selected_template else None

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

        copy_to_clipboard = (
            (
                Prompt.ask(
                    f"\n[bold {theme.WARNING}]Copy to clipboard?[/bold {theme.WARNING}]",
                    default="y",
                    choices=["y", "n"],
                )
                or ""
            )
            .lower()
            .strip()
        )
        if copy_to_clipboard in ["y", "yes"]:
            try:
                pyperclip.copy(result.summary)
                console.print(
                    f"[bold {theme.SECONDARY}]✓ Summary copied to clipboard![/bold {theme.SECONDARY}]"
                )
            except Exception as e:
                console.print(
                    f"[bold {theme.ERROR}]✗ Failed to copy to clipboard: {e}[/bold {theme.ERROR}]"
                )
