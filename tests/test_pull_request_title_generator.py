"""Tests for conventional-commit PR title generation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from usepr.modules.pull_request_title_generator import PullRequestTitleGeneratorModule
from usepr.services.pr_summary_service import TitleResult, generate_title
from usepr.signatures.pull_request_title_generator import (
    CONVENTIONAL_COMMIT_TYPES,
    RULES,
)


class TestSignature:
    def test_rules_is_nonempty(self) -> None:
        assert RULES
        assert all(isinstance(rule, str) and rule for rule in RULES)

    def test_all_conventional_types_are_allowed(self) -> None:
        types_text = " ".join(RULES)
        for commit_type in CONVENTIONAL_COMMIT_TYPES:
            assert commit_type in types_text

    def test_rules_require_single_line_format(self) -> None:
        rules_text = " ".join(RULES).lower()
        assert "single" in rules_text or "one line" in rules_text
        assert "technical" not in rules_text


class TestModule:
    @patch("usepr.modules.pull_request_title_generator.dspy.ChainOfThought")
    def test_forwards_inputs_and_rules(self, mock_cot: MagicMock) -> None:
        predictor = MagicMock()
        predictor.return_value = MagicMock(
            reasoning="r", title="feat(auth): add token refresh"
        )
        mock_cot.return_value = predictor

        module = PullRequestTitleGeneratorModule()
        result = module.forward(
            commits=["feat: add token refresh"],
            related_issues="#42",
            branch_name="feature/token-refresh",
        )

        predictor.assert_called_once_with(
            commits=["feat: add token refresh"],
            rules=RULES,
            related_issues="#42",
            branch_name="feature/token-refresh",
        )
        assert result.title == "feat(auth): add token refresh"


class TestGenerateTitle:
    @patch("usepr.services.pr_summary_service.PullRequestTitleGeneratorModule")
    def test_returns_trimmed_title_result(self, mock_module_cls: MagicMock) -> None:
        module = MagicMock()
        module.return_value = MagicMock(
            reasoning="chose feat", title="  feat: add login  \n"
        )
        mock_module_cls.return_value = module

        result = generate_title(
            commits=["feat: add login"],
            related_issues="#7",
            branch_name="feature/login",
        )

        module.assert_called_once_with(
            commits=["feat: add login"],
            related_issues="#7",
            branch_name="feature/login",
        )
        assert result == TitleResult(reasoning="chose feat", title="feat: add login")

    @patch("usepr.services.pr_summary_service.PullRequestTitleGeneratorModule")
    def test_optional_inputs_default_to_none(self, mock_module_cls: MagicMock) -> None:
        module = MagicMock()
        module.return_value = MagicMock(reasoning="r", title="fix: repair parser")
        mock_module_cls.return_value = module

        generate_title(commits=["fix: repair parser"])

        module.assert_called_once_with(
            commits=["fix: repair parser"],
            related_issues=None,
            branch_name=None,
        )
