import dspy

from usepr.signatures.pull_request_summary_generator import (
    RULES,
    TEMPLATE_RULES,
    PullRequestSummaryGeneratorSignature,
)


class PullRequestSummaryGeneratorModule(dspy.Module):
    def __init__(self, callbacks=None):
        super().__init__(callbacks)
        self.diff_to_pull_request_summary = dspy.ChainOfThought(
            PullRequestSummaryGeneratorSignature
        )

    def forward(
        self,
        commits: str,
        related_issues: str | None = None,
        template: str | None = None,
    ):
        if template:
            rules = TEMPLATE_RULES
        elif not related_issues or not related_issues.strip():
            rules = RULES[2:]
        else:
            rules = RULES
        result = self.diff_to_pull_request_summary(
            commits=commits,
            rules=rules,
            related_issues=related_issues,
            template=template,
        )
        return result
