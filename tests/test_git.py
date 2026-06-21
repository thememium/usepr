"""Tests for usepr.utils.git module."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from usepr.utils.git import (
    ensure_git_repo,
    get_commits_between,
    get_default_branch,
    parse_commits,
    resolve_ref,
    run,
)

# ---------------------------------------------------------------------------
# parse_commits (pure function – zero mocking needed)
# ---------------------------------------------------------------------------


class TestParseCommits:
    def test_single_commit(self) -> None:
        text = "feat: add login"
        assert parse_commits(text) == ["feat: add login"]

    def test_multiple_commits(self) -> None:
        text = "feat: add login----fix: typo----docs: readme"
        assert parse_commits(text) == [
            "feat: add login",
            "fix: typo",
            "docs: readme",
        ]

    def test_strips_whitespace(self) -> None:
        text = "  feat: one  ----  fix: two  "
        assert parse_commits(text) == ["feat: one", "fix: two"]

    def test_triple_separator_produces_empty_segment(self) -> None:
        text = "feat: one------fix: two"
        result = parse_commits(text)
        assert result[0] == "feat: one"
        assert len(result) == 2

    def test_empty_string(self) -> None:
        assert parse_commits("") == []

    def test_only_separators(self) -> None:
        assert parse_commits("----") == []

    def test_multiline_commit_body(self) -> None:
        text = "feat: big change\n\nBody paragraph here----fix: small fix"
        result = parse_commits(text)
        assert len(result) == 2
        assert "feat: big change" in result[0]
        assert "Body paragraph here" in result[0]

    def test_trailing_separator_stripped_by_get_commits_between(self) -> None:
        """The trailing ---- is removed by get_commits_between, not parse_commits.
        parse_commits should still handle it gracefully."""
        text = "feat: one----"
        # parse_commits doesn't strip trailing ----, it just splits
        result = parse_commits(text)
        assert "feat: one" in result


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------


class TestRun:
    @patch("subprocess.check_output")
    def test_returns_stripped_output(self, mock_check: MagicMock) -> None:
        mock_check.return_value = b"  some output  \n"
        assert run(["git", "status"]) == "some output"

    @patch("subprocess.check_output")
    def test_passes_cwd(self, mock_check: MagicMock) -> None:
        mock_check.return_value = b"ok"
        run(["git", "log"], cwd="/some/path")
        mock_check.assert_called_once_with(
            ["git", "log"], stderr=subprocess.STDOUT, cwd="/some/path"
        )

    @patch("subprocess.check_output")
    def test_raises_on_failure(self, mock_check: MagicMock) -> None:
        mock_check.side_effect = subprocess.CalledProcessError(1, "git")
        with pytest.raises(subprocess.CalledProcessError):
            run(["git", "bad-command"])

    @patch("subprocess.check_output")
    def test_handles_non_utf8_bytes(self, mock_check: MagicMock) -> None:
        # errors="replace" means non-decodable bytes become replacement char
        mock_check.return_value = b"\xff\xfe"
        result = run(["git", "log"])
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# ensure_git_repo()
# ---------------------------------------------------------------------------


class TestEnsureGitRepo:
    @patch("usepr.utils.git.run")
    def test_valid_repo_does_not_exit(self, mock_run: MagicMock) -> None:
        mock_run.return_value = "true"
        # Should not raise or exit
        ensure_git_repo("/valid/repo")

    @patch("usepr.utils.git.run")
    def test_invalid_repo_exits(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        with pytest.raises(SystemExit) as exc_info:
            ensure_git_repo("/not/a/repo")
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# get_default_branch()
# ---------------------------------------------------------------------------


class TestGetDefaultBranch:
    @patch("subprocess.run")
    def test_returns_main_from_symbolic_ref(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = "refs/remotes/origin/main\n"
        result_mock.returncode = 0
        mock_run.return_value = result_mock

        assert get_default_branch("/repo") == "main"

    @patch("subprocess.run")
    def test_returns_master_from_symbolic_ref(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = "refs/remotes/origin/master\n"
        result_mock.returncode = 0
        mock_run.return_value = result_mock

        assert get_default_branch("/repo") == "master"

    @patch("subprocess.run")
    def test_fallback_to_main_branch(self, mock_run: MagicMock) -> None:
        # First call (symbolic-ref with check=True) raises CalledProcessError
        # Second call (show-ref for main with check=True) succeeds
        success_result = MagicMock()
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "git"),
            success_result,
        ]

        assert get_default_branch("/repo") == "main"

    @patch("subprocess.run")
    def test_fallback_to_master_branch(self, mock_run: MagicMock) -> None:
        # All calls fail -> returns "master"
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        assert get_default_branch("/repo") == "master"


# ---------------------------------------------------------------------------
# resolve_ref()
# ---------------------------------------------------------------------------


class TestResolveRef:
    @patch("subprocess.run")
    def test_resolves_bare_ref(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.returncode = 0
        mock_run.return_value = result_mock

        assert resolve_ref("/repo", "main") == "main"

    @patch("subprocess.run")
    def test_resolves_origin_ref(self, mock_run: MagicMock) -> None:
        # First call (bare ref) fails, second (origin/ref) succeeds
        fail = MagicMock(returncode=1)
        success = MagicMock(returncode=0)
        mock_run.side_effect = [fail, success]

        assert resolve_ref("/repo", "feature-branch") == "origin/feature-branch"

    @patch("subprocess.run")
    def test_exits_on_unresolvable_ref(self, mock_run: MagicMock) -> None:
        fail = MagicMock(returncode=1)
        mock_run.return_value = fail

        with pytest.raises(SystemExit) as exc_info:
            resolve_ref("/repo", "nonexistent")
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# get_commits_between()
# ---------------------------------------------------------------------------


class TestGetCommitsBetween:
    @patch("subprocess.run")
    def test_returns_cleaned_output(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = "feat: one\n\nBody----feat: two----"
        mock_run.return_value = result_mock

        output = get_commits_between("/repo", "v1.0.0", "HEAD")
        assert output.endswith("feat: two")
        assert not output.endswith("----")

    @patch("subprocess.run")
    def test_uses_default_branch_when_no_prev_tag(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = "feat: one----"
        mock_run.return_value = result_mock

        # When prev_tag is None, it calls get_default_branch
        with patch("usepr.utils.git.get_default_branch", return_value="main"):
            get_commits_between("/repo", None, "HEAD")

        # Should have been called with main..HEAD range
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "main..HEAD" in cmd[-1]

    @patch("subprocess.run")
    def test_format_includes_subject_and_body(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = ""
        mock_run.return_value = result_mock

        with patch("usepr.utils.git.get_default_branch", return_value="main"):
            get_commits_between("/repo", "main", "HEAD")

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        # Check format string includes %s and %b
        fmt_arg = [a for a in cmd if a.startswith("--format=")][0]
        assert "%s" in fmt_arg
        assert "%b" in fmt_arg

    @patch("subprocess.run")
    def test_no_trailing_separator_in_output(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = "feat: one----feat: two----"
        mock_run.return_value = result_mock

        output = get_commits_between("/repo", "v1.0", "HEAD")
        assert not output.endswith("----")

    @patch("subprocess.run")
    def test_empty_commits_returns_empty_string(self, mock_run: MagicMock) -> None:
        result_mock = MagicMock()
        result_mock.stdout = ""
        mock_run.return_value = result_mock

        assert get_commits_between("/repo", "v1.0", "HEAD") == ""
