import dspy

from usepr.signatures.pull_request_title_generator import (
    RULES,
    PullRequestTitleGeneratorSignature,
)


class PullRequestTitleGeneratorModule(dspy.Module):
    def __init__(self, callbacks=None):
        super().__init__(callbacks)
        self.commits_to_pull_request_title = dspy.ChainOfThought(
            PullRequestTitleGeneratorSignature
        )

    def forward(
        self,
        commits: list[str],
        related_issues: str | None = None,
        branch_name: str | None = None,
    ):
        result = self.commits_to_pull_request_title(
            commits=commits,
            rules=RULES,
            related_issues=related_issues,
            branch_name=branch_name,
        )
        return result
