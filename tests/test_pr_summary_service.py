"""Tests for usepr.services.pr_summary_service module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from usepr.services.pr_summary_service import (
    CommitContext,
    SummaryResult,
    gather_commits,
    generate_summary,
    get_default_branch_name,
    get_templates,
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


class TestDataclasses:
    def test_summary_result_fields(self) -> None:
        r = SummaryResult(reasoning="r", summary="s")
        assert r.reasoning == "r"
        assert r.summary == "s"

    def test_commit_context_fields(self) -> None:
        ctx = CommitContext(
            commits=["a", "b"], base_branch="main", default_branch="main"
        )
        assert ctx.commits == ["a", "b"]
        assert ctx.base_branch == "main"
        assert ctx.default_branch == "main"


# ---------------------------------------------------------------------------
# get_default_branch_name()
# ---------------------------------------------------------------------------


class TestGetDefaultBranchName:
    @patch("usepr.services.pr_summary_service.get_default_branch")
    def test_delegates_and_strips(self, mock_get: MagicMock) -> None:
        mock_get.return_value = "  main  \n"
        assert get_default_branch_name("/repo") == "main"
        mock_get.assert_called_once_with("/repo")


# ---------------------------------------------------------------------------
# gather_commits()
# ---------------------------------------------------------------------------


class TestGatherCommits:
    @patch("usepr.services.pr_summary_service.parse_commits")
    @patch("usepr.services.pr_summary_service.get_commits_between")
    @patch("usepr.services.pr_summary_service.resolve_ref")
    @patch("usepr.services.pr_summary_service.get_default_branch_name")
    @patch("usepr.services.pr_summary_service.ensure_git_repo")
    def test_happy_path(
        self,
        mock_ensure: MagicMock,
        mock_default: MagicMock,
        mock_resolve: MagicMock,
        mock_between: MagicMock,
        mock_parse: MagicMock,
    ) -> None:
        mock_default.return_value = "main"
        mock_resolve.return_value = "main"
        mock_between.return_value = "feat: one----fix: two"
        mock_parse.return_value = ["feat: one", "fix: two"]

        ctx = gather_commits("/repo", "main")

        mock_ensure.assert_called_once_with("/repo")
        mock_resolve.assert_called_once_with("/repo", "main")
        mock_between.assert_called_once_with("/repo", "main", "HEAD")
        assert ctx.commits == ["feat: one", "fix: two"]
        assert ctx.base_branch == "main"
        assert ctx.default_branch == "main"

    @patch("usepr.services.pr_summary_service.parse_commits")
    @patch("usepr.services.pr_summary_service.get_commits_between")
    @patch("usepr.services.pr_summary_service.resolve_ref")
    @patch("usepr.services.pr_summary_service.get_default_branch_name")
    @patch("usepr.services.pr_summary_service.ensure_git_repo")
    def test_empty_commits(
        self,
        mock_ensure: MagicMock,
        mock_default: MagicMock,
        mock_resolve: MagicMock,
        mock_between: MagicMock,
        mock_parse: MagicMock,
    ) -> None:
        mock_default.return_value = "main"
        mock_resolve.return_value = "main"
        mock_between.return_value = ""
        mock_parse.return_value = []

        ctx = gather_commits("/repo", "main")
        assert ctx.commits == []

    @patch("usepr.services.pr_summary_service.ensure_git_repo")
    def test_propagates_system_exit_on_invalid_repo(
        self, mock_ensure: MagicMock
    ) -> None:
        mock_ensure.side_effect = SystemExit(2)
        with pytest.raises(SystemExit):
            gather_commits("/bad/repo", "main")


# ---------------------------------------------------------------------------
# generate_summary()
# ---------------------------------------------------------------------------


class TestGenerateSummary:
    @patch("usepr.services.pr_summary_service.PullRequestSummaryGeneratorModule")
    def test_returns_summary_result(self, mock_module_cls: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.reasoning = "step by step"
        mock_result.summary = "# Summary\n\nChanges here"
        mock_instance.return_value = mock_result
        mock_module_cls.return_value = mock_instance

        result = generate_summary(commits=["feat: one", "fix: two"])

        assert isinstance(result, SummaryResult)
        assert result.reasoning == "step by step"
        assert result.summary == "# Summary\n\nChanges here"

    @patch("usepr.services.pr_summary_service.PullRequestSummaryGeneratorModule")
    def test_passes_all_args_to_module(self, mock_module_cls: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(reasoning="r", summary="s")
        mock_module_cls.return_value = mock_instance

        generate_summary(
            commits=["c1"],
            related_issues="#123",
            template="## Description",
        )

        mock_instance.assert_called_once_with(
            commits=["c1"],
            related_issues="#123",
            template="## Description",
        )

    @patch("usepr.services.pr_summary_service.PullRequestSummaryGeneratorModule")
    def test_none_optional_args(self, mock_module_cls: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(reasoning="r", summary="s")
        mock_module_cls.return_value = mock_instance

        generate_summary(commits=["c1"])

        mock_instance.assert_called_once_with(
            commits=["c1"],
            related_issues=None,
            template=None,
        )


# ---------------------------------------------------------------------------
# get_templates()
# ---------------------------------------------------------------------------


class TestGetTemplates:
    @patch("usepr.services.pr_summary_service.find_pr_templates")
    def test_delegates_to_find_pr_templates(self, mock_find: MagicMock) -> None:
        mock_find.return_value = []
        result = get_templates("/repo")
        mock_find.assert_called_once_with("/repo")
        assert result == []

    @patch("usepr.services.pr_summary_service.find_pr_templates")
    def test_returns_templates(self, mock_find: MagicMock) -> None:
        from usepr.utils.github import PrTemplate

        tpl = PrTemplate(path="/x", content="c", name="n")
        mock_find.return_value = [tpl]
        result = get_templates("/repo")
        assert result == [tpl]
