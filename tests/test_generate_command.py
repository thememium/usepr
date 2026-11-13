"""Tests for usepr.cli.commands.generate_command module."""

from __future__ import annotations

import os
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pyperclip
import pytest
import typer

from usepr.cli.commands.generate_command import OTHER_BRANCH, GenerateCommand
from usepr.services.pr_summary_service import CommitContext, SummaryResult
from usepr.utils.github import PrTemplate

MODULE = "usepr.cli.commands.generate_command"


def _command() -> GenerateCommand:
    return GenerateCommand(typer.Typer())


def _template(
    path: str = ".github/PULL_REQUEST_TEMPLATE.md",
    content: str = "PR body",
    name: str | None = None,
) -> PrTemplate:
    return PrTemplate(path=path, content=content, name=name)


@pytest.fixture
def deps() -> Iterator[dict[str, MagicMock]]:
    with (
        patch(f"{MODULE}.console") as console,
        patch(f"{MODULE}.configure_dspy") as configure_dspy,
        patch(f"{MODULE}.Menu") as menu,
        patch(f"{MODULE}.Prompt") as prompt,
        patch(f"{MODULE}.Spinner") as spinner,
        patch(f"{MODULE}.gather_commits") as gather_commits,
        patch(f"{MODULE}.get_templates") as get_templates,
        patch(f"{MODULE}.generate_summary") as generate_summary,
        patch(f"{MODULE}.pyperclip.copy") as copy,
        patch(
            "usepr.utils.git.get_default_branch", return_value="main"
        ) as get_default_branch,
        patch(
            "usepr.utils.git.get_branch_selection_options",
            return_value=["main", "dev"],
        ) as get_branch_selection_options,
    ):
        menu.select.return_value = "main"
        prompt.ask.return_value = "y"
        spinner.return_value = MagicMock()
        gather_commits.return_value = CommitContext(
            commits=["abc123"], base_branch="main", default_branch="main"
        )
        get_templates.return_value = []
        generate_summary.return_value = SummaryResult(
            reasoning="reasoning", summary="## Title"
        )
        yield {
            "console": console,
            "configure_dspy": configure_dspy,
            "menu": menu,
            "prompt": prompt,
            "spinner": spinner,
            "gather_commits": gather_commits,
            "get_templates": get_templates,
            "generate_summary": generate_summary,
            "copy": copy,
            "get_default_branch": get_default_branch,
            "get_branch_selection_options": get_branch_selection_options,
        }


class TestMetadata:
    def test_signature(self) -> None:
        assert _command().signature() == "generate"

    def test_description(self) -> None:
        assert _command().description() == "Description for generate command"

    def test_aliases(self) -> None:
        assert _command().aliases() == ["gen"]


class TestPromptForTemplate:
    @patch(f"{MODULE}.Prompt")
    def test_no_templates_returns_none(self, mock_prompt: MagicMock) -> None:
        assert _command()._prompt_for_template([]) is None
        mock_prompt.ask.assert_not_called()

    @patch(f"{MODULE}.Prompt")
    def test_single_template_accepted(self, mock_prompt: MagicMock) -> None:
        t = _template()
        mock_prompt.ask.return_value = " Y "
        assert _command()._prompt_for_template([t]) is t
        assert "PULL_REQUEST_TEMPLATE.md" in mock_prompt.ask.call_args.args[0]

    @patch(f"{MODULE}.Prompt")
    def test_single_template_declined(self, mock_prompt: MagicMock) -> None:
        mock_prompt.ask.return_value = "n"
        assert _command()._prompt_for_template([_template()]) is None

    @patch(f"{MODULE}.Prompt")
    def test_single_template_empty_answer(self, mock_prompt: MagicMock) -> None:
        mock_prompt.ask.return_value = None
        assert _command()._prompt_for_template([_template()]) is None

    @patch(f"{MODULE}.console")
    @patch(f"{MODULE}.Prompt")
    def test_multiple_templates_selects_by_number(
        self, mock_prompt: MagicMock, mock_console: MagicMock
    ) -> None:
        named = _template(
            path=".github/PULL_REQUEST_TEMPLATE/feature.md", name="Feature"
        )
        unnamed = _template(path=".github/PULL_REQUEST_TEMPLATE/bug.md")
        mock_prompt.ask.return_value = "2"
        assert _command()._prompt_for_template([named, unnamed]) is unnamed
        assert mock_console.print.call_count == 4

    @patch(f"{MODULE}.console")
    @patch(f"{MODULE}.Prompt")
    def test_multiple_templates_skip_zero(
        self, mock_prompt: MagicMock, mock_console: MagicMock
    ) -> None:
        mock_prompt.ask.return_value = "0"
        assert _command()._prompt_for_template([_template(), _template()]) is None
        assert mock_console.print.call_count == 4

    @patch(f"{MODULE}.console")
    @patch(f"{MODULE}.Prompt")
    def test_multiple_templates_empty_choice(
        self, mock_prompt: MagicMock, mock_console: MagicMock
    ) -> None:
        mock_prompt.ask.return_value = ""
        assert _command()._prompt_for_template([_template(), _template()]) is None
        assert mock_console.print.call_count == 4

    @patch(f"{MODULE}.console")
    @patch(f"{MODULE}.Prompt")
    def test_multiple_templates_non_numeric(
        self, mock_prompt: MagicMock, mock_console: MagicMock
    ) -> None:
        mock_prompt.ask.return_value = "nope"
        assert _command()._prompt_for_template([_template(), _template()]) is None
        assert mock_console.print.call_count == 4

    @patch(f"{MODULE}.console")
    @patch(f"{MODULE}.Prompt")
    def test_multiple_templates_out_of_range(
        self, mock_prompt: MagicMock, mock_console: MagicMock
    ) -> None:
        mock_prompt.ask.return_value = "99"
        assert _command()._prompt_for_template([_template(), _template()]) is None
        assert mock_console.print.call_count == 4


class TestHandle:
    def test_aborts_when_no_branch_selected(self, deps: dict[str, MagicMock]) -> None:
        deps["menu"].select.return_value = None

        _command().handle()

        deps["configure_dspy"].assert_called_once_with(None)
        deps["gather_commits"].assert_not_called()
        deps["menu"].select.assert_called_once()

    def test_custom_branch_stops_when_no_commits(
        self, deps: dict[str, MagicMock]
    ) -> None:
        repo = os.path.abspath(".")
        deps["menu"].select.return_value = OTHER_BRANCH
        deps["prompt"].ask.return_value = "  dev  "
        deps["gather_commits"].return_value = CommitContext(
            commits=[], base_branch="dev", default_branch="main"
        )

        _command().handle(model="openrouter/test")

        deps["configure_dspy"].assert_called_once_with("openrouter/test")
        deps["get_branch_selection_options"].assert_called_once_with(repo, "main")
        deps["gather_commits"].assert_called_once_with(repo, "dev")
        deps["generate_summary"].assert_not_called()

    def test_successful_generation_and_copy(self, deps: dict[str, MagicMock]) -> None:
        deps["prompt"].ask.side_effect = ["issue-42", "y", "y"]
        deps["get_templates"].return_value = [_template(content="Use this template")]

        _command().handle()

        deps["get_templates"].assert_called_once_with(os.path.abspath("."))
        deps["generate_summary"].assert_called_once_with(
            commits=["abc123"],
            related_issues="issue-42",
            template="Use this template",
        )
        deps["copy"].assert_called_once_with("## Title")

    def test_declines_clipboard_when_answer_blank(
        self, deps: dict[str, MagicMock]
    ) -> None:
        deps["prompt"].ask.side_effect = ["", None]

        _command().handle()

        deps["copy"].assert_not_called()

    def test_reports_clipboard_failure(self, deps: dict[str, MagicMock]) -> None:
        deps["prompt"].ask.side_effect = ["", "y"]
        deps["copy"].side_effect = pyperclip.PyperclipException("no clipboard")

        _command().handle()

        assert any(
            "Failed to copy" in str(call)
            for call in deps["console"].print.call_args_list
        )
