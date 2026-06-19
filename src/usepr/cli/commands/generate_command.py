"""GenerateCommand - CLI command."""

from __future__ import annotations

import os

import pyperclip
from rich.panel import Panel
from rich.syntax import Syntax
from usecli import BaseCommand, Prompt, console, theme

from usepr.modules.pull_request_summary_generator import (
    PullRequestSummaryGeneratorModule,
)
from usepr.utils.git import (
    ensure_git_repo,
    get_commits_between,
    get_default_branch,
    parse_commits,
    resolve_ref,
)


class GenerateCommand(BaseCommand):
    def signature(self) -> str:
        return "generate"

    def description(self) -> str:
        return "Description for generate command"

    def aliases(self) -> list[str]:
        return ["gen"]

    def handle(
        self,
    ) -> None:

        # Get absolute path and verify it's a git repo
        repo_path = "."  # Current directory
        repo = os.path.abspath(repo_path)
        ensure_git_repo(repo)

        console.clear()
        console.print(f"[bold {theme.PRIMARY}]Pull Request Summary Generator")

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

        prev_tag = resolve_ref(repo, base_branch)
        latest_tag = "HEAD"

        commit_text = get_commits_between(repo, prev_tag, latest_tag)
        commits = parse_commits(commit_text)

        if not commits:
            console.print(
                "[red]No commits found between the specified tags or branches."
            )
            return

        proceed = Prompt.ask(
            "Do you want to proceed with generating the summary?",
            default="y",
            choices=["y", "n"],
            show_choices=False,
        )
        if proceed and proceed.lower() != "y":
            console.print("Aborting summary generation.")
            return

        related_issues = Prompt.ask(
            "List any related issues or tasks (comma-separated), or leave blank if none:",
            default="",
        )

        program = PullRequestSummaryGeneratorModule()
        result = program(commits=commits, related_issues=related_issues)

        # Print reasoning and summary using rich
        summary_md = Syntax(
            result.summary,
            "markdown",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        console.print(
            Panel(
                summary_md, title="Pull Request Summary", border_style=theme.SECONDARY
            )
        )

        # Ask if user wants to copy to clipboard
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
