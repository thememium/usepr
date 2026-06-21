"""Tests for usepr.modules.pull_request_summary_generator module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from usepr.modules.pull_request_summary_generator import (
    PullRequestSummaryGeneratorModule,
)
from usepr.signatures.pull_request_summary_generator import RULES, TEMPLATE_RULES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestSignatureConstants:
    def test_rules_is_nonempty_list(self) -> None:
        assert isinstance(RULES, list)
        assert len(RULES) > 0

    def test_template_rules_is_nonempty_list(self) -> None:
        assert isinstance(TEMPLATE_RULES, list)
        assert len(TEMPLATE_RULES) > 0

    def test_rules_are_strings(self) -> None:
        for rule in RULES:
            assert isinstance(rule, str)
            assert len(rule) > 0

    def test_template_rules_are_strings(self) -> None:
        for rule in TEMPLATE_RULES:
            assert isinstance(rule, str)
            assert len(rule) > 0

    def test_rules_start_with_summary_header_rule(self) -> None:
        assert any("Summary header" in r or "summary" in r.lower() for r in RULES)

    def test_template_rules_mention_template(self) -> None:
        assert any("template" in r.lower() for r in TEMPLATE_RULES)


# ---------------------------------------------------------------------------
# PullRequestSummaryGeneratorModule – rule selection logic
# ---------------------------------------------------------------------------


class TestModuleRuleSelection:
    """Test the conditional logic that picks which rules to pass."""

    def _get_rules_passed(
        self,
        template: str | None = None,
        related_issues: str | None = None,
    ) -> list[str]:
        """Helper: instantiate module, call forward, capture rules arg."""
        # We mock the actual ChainOfThought call to inspect what rules were passed
        with patch(
            "usepr.modules.pull_request_summary_generator.dspy.ChainOfThought"
        ) as mock_cot:
            mock_predictor = MagicMock()
            mock_predictor.return_value = MagicMock(reasoning="r", summary="s")
            mock_cot.return_value = mock_predictor

            module = PullRequestSummaryGeneratorModule()
            module.forward(
                commits="feat: one",
                related_issues=related_issues,
                template=template,
            )

            call_kwargs = mock_predictor.call_args[1]
            return call_kwargs["rules"]

    def test_template_present_uses_template_rules(self) -> None:
        rules = self._get_rules_passed(template="## Description")
        assert rules == TEMPLATE_RULES

    def test_no_issues_uses_rules_from_index_2(self) -> None:
        rules = self._get_rules_passed(related_issues=None)
        assert rules == RULES[2:]

    def test_empty_issues_uses_rules_from_index_2(self) -> None:
        rules = self._get_rules_passed(related_issues="")
        assert rules == RULES[2:]

    def test_whitespace_issues_uses_rules_from_index_2(self) -> None:
        rules = self._get_rules_passed(related_issues="   ")
        assert rules == RULES[2:]

    def test_issues_present_uses_full_rules(self) -> None:
        rules = self._get_rules_passed(related_issues="#123")
        assert rules == RULES

    def test_template_overrides_issues(self) -> None:
        """Even with issues, template takes priority."""
        rules = self._get_rules_passed(template="## Desc", related_issues="#123")
        assert rules == TEMPLATE_RULES


# ---------------------------------------------------------------------------
# PullRequestSummaryGeneratorModule – integration-ish
# ---------------------------------------------------------------------------


class TestModuleForward:
    @patch("usepr.modules.pull_request_summary_generator.dspy.ChainOfThought")
    def test_returns_chain_of_thought_result(self, mock_cot: MagicMock) -> None:
        mock_predictor = MagicMock()
        expected = MagicMock(reasoning="step by step", summary="# Summary")
        mock_predictor.return_value = expected
        mock_cot.return_value = mock_predictor

        module = PullRequestSummaryGeneratorModule()
        result = module.forward(commits="feat: one", related_issues="#1")

        assert result.reasoning == "step by step"
        assert result.summary == "# Summary"

    @patch("usepr.modules.pull_request_summary_generator.dspy.ChainOfThought")
    def test_passes_commits_as_positional(self, mock_cot: MagicMock) -> None:
        mock_predictor = MagicMock()
        mock_predictor.return_value = MagicMock(reasoning="r", summary="s")
        mock_cot.return_value = mock_predictor

        module = PullRequestSummaryGeneratorModule()
        module.forward(commits="feat: one----fix: two", related_issues="#1")

        call_kwargs = mock_predictor.call_args[1]
        assert call_kwargs["commits"] == "feat: one----fix: two"

    @patch("usepr.modules.pull_request_summary_generator.dspy.ChainOfThought")
    def test_passes_related_issues(self, mock_cot: MagicMock) -> None:
        mock_predictor = MagicMock()
        mock_predictor.return_value = MagicMock(reasoning="r", summary="s")
        mock_cot.return_value = mock_predictor

        module = PullRequestSummaryGeneratorModule()
        module.forward(commits="c", related_issues="#42, #43")

        call_kwargs = mock_predictor.call_args[1]
        assert call_kwargs["related_issues"] == "#42, #43"

    @patch("usepr.modules.pull_request_summary_generator.dspy.ChainOfThought")
    def test_passes_template(self, mock_cot: MagicMock) -> None:
        mock_predictor = MagicMock()
        mock_predictor.return_value = MagicMock(reasoning="r", summary="s")
        mock_cot.return_value = mock_predictor

        module = PullRequestSummaryGeneratorModule()
        module.forward(commits="c", template="## Description\n\n...")

        call_kwargs = mock_predictor.call_args[1]
        assert call_kwargs["template"] == "## Description\n\n..."
