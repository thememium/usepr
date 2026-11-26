"""Tests for usepr.cli.commands.generate_command module."""

from __future__ import annotations

import os
from collections.abc import Iterator
from unittest.mock import MagicMock, call, patch

import pyperclip
import pytest
import typer

from usepr.cli.commands.generate_command import OTHER_BRANCH, GenerateCommand
from usepr.services.pr_summary_service import CommitContext, SummaryResult, TitleResult
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
        patch(f"{MODULE}.generate_title") as generate_title,
        patch(f"{MODULE}.pyperclip.copy") as copy,
        patch("usepr.utils.git.ensure_git_repo") as ensure_git_repo,
        patch(
            "usepr.utils.git.get_default_branch", return_value="main"
        ) as get_default_branch,
        patch(
            "usepr.utils.git.get_current_branch", return_value="feature/x"
        ) as get_current_branch,
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
        generate_title.return_value = TitleResult(
            reasoning="title reasoning", title="feat: add thing"
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
            "generate_title": generate_title,
            "copy": copy,
            "ensure_git_repo": ensure_git_repo,
            "get_default_branch": get_default_branch,
            "get_current_branch": get_current_branch,
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
    def test_aborts_outside_git_repo(self, deps: dict[str, MagicMock]) -> None:
        deps["ensure_git_repo"].side_effect = SystemExit(2)

        with pytest.raises(SystemExit) as exc_info:
            _command().handle()

        assert exc_info.value.code == 2
        deps["ensure_git_repo"].assert_called_once_with(os.path.abspath("."))
        deps["configure_dspy"].assert_not_called()
        deps["menu"].select.assert_not_called()

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
        deps["generate_title"].assert_not_called()
        deps["generate_summary"].assert_not_called()

    def test_successful_generation_and_copy(self, deps: dict[str, MagicMock]) -> None:
        deps["prompt"].ask.side_effect = ["issue-42", "y", "y", "y"]
        deps["get_templates"].return_value = [_template(content="Use this template")]

        _command().handle()

        deps["get_templates"].assert_called_once_with(os.path.abspath("."))
        deps["generate_title"].assert_called_once_with(
            commits=["abc123"],
            related_issues="issue-42",
            branch_name="feature/x",
        )
        deps["generate_summary"].assert_called_once_with(
            commits=["abc123"],
            related_issues="issue-42",
            template="Use this template",
        )
        deps["copy"].assert_has_calls([call("feat: add thing"), call("## Title")])

    def test_title_generated_before_summary(self, deps: dict[str, MagicMock]) -> None:
        manager = MagicMock()
        manager.attach_mock(deps["generate_title"], "generate_title")
        manager.attach_mock(deps["generate_summary"], "generate_summary")
        deps["prompt"].ask.side_effect = ["", "", ""]

        _command().handle()

        assert [c[0] for c in manager.mock_calls] == [
            "generate_title",
            "generate_summary",
        ]

    def test_passes_none_branch_when_detached(self, deps: dict[str, MagicMock]) -> None:
        deps["get_current_branch"].return_value = ""
        deps["prompt"].ask.side_effect = ["", "", ""]

        _command().handle()

        deps["generate_title"].assert_called_once_with(
            commits=["abc123"],
            related_issues="",
            branch_name=None,
        )

    def test_declines_clipboard_when_answer_blank(
        self, deps: dict[str, MagicMock]
    ) -> None:
        deps["prompt"].ask.side_effect = ["", "", None]

        _command().handle()

        deps["copy"].assert_not_called()

    def test_declines_title_copy_but_copies_summary(
        self, deps: dict[str, MagicMock]
    ) -> None:
        deps["prompt"].ask.side_effect = ["", "n", "y"]

        _command().handle()

        deps["copy"].assert_called_once_with("## Title")

    def test_reports_clipboard_failure(self, deps: dict[str, MagicMock]) -> None:
        deps["prompt"].ask.side_effect = ["", "", "y"]
        deps["copy"].side_effect = pyperclip.PyperclipException("no clipboard")

        _command().handle()

        assert any(
            "Failed to copy summary" in str(call)
            for call in deps["console"].print.call_args_list
        )
