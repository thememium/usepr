import dspy
from typing import List, Optional

RULES = [
    "Start the summary with a # Summary header.",
    "The next section should be ## Linked Issues, listing any related issues or tasks.",
    "Follow with a ## Description section that details the changes made in the pull request.",
    "Use bullet points for each major change.",
    "Keep the summary concise and to the point.",
    "Highlight any breaking changes or important updates.",
    "Avoid technical jargon; use clear and simple language.",
]

class PullRequestSummaryGeneratorSignature(dspy.Signature):
    """Generate a concise summary of a pull request based on a list of conventional commit messages. The summary should highlight the main changes introduced by the commits, and may include markdown tables or mermaid diagrams for better visualization when appropriate."""

    rules: List[str] = dspy.InputField(desc="A list of rules to follow when generating the summary.")
    commits: List[str] = dspy.InputField(desc="A list of conventional commit messages.")
    related_issues: Optional[str] = dspy.InputField(default=None, desc="A list of related issues or tasks, if any.")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning about the commits and how they contribute to the summary.")
    summary: str = dspy.OutputField(desc="A summary of the pull request based on the provided commits.")
