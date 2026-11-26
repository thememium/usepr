import dspy

CONVENTIONAL_COMMIT_TYPES = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]

RULES = [
    (
        "Output exactly one line in the Conventional Commits v1.0.0 format: "
        "'<type>[optional scope][optional !]: <description>'."
    ),
    (f"Use exactly one type from this list: {', '.join(CONVENTIONAL_COMMIT_TYPES)}."),
    (
        "Put the scope in parentheses immediately after the type, for example "
        "'fix(parser): ...'; omit the scope when it adds no useful context."
    ),
    (
        "Add '!' immediately before the colon for a breaking change, for example "
        "'feat(api)!: ...'."
    ),
    (
        "Start the description with a lowercase letter, use imperative mood, "
        "and do not end it with a period."
    ),
    "Do not use any other punctuation or formatting around the title: no quotes, no backticks, no markdown, no 'Title:' prefix.",
    "Keep the whole title at or under 72 characters.",
    (
        "Use the branch name only as extra context for intent; never copy the "
        "branch name verbatim into the title."
    ),
    ("For a revert, use the type 'revert' and describe the reverted change."),
    "Never include reasoning, bullet points, or additional lines in the title.",
]


class PullRequestTitleGeneratorSignature(dspy.Signature):
    """Generate a pull request title from conventional commit messages, following Conventional Commits v1.0.0 strictly. The title should describe the overall change introduced by the branch and must be a single valid conventional commit header line."""

    rules: list[str] = dspy.InputField(
        desc="A list of rules to follow when generating the title."
    )
    commits: list[str] = dspy.InputField(desc="A list of conventional commit messages.")
    related_issues: str | None = dspy.InputField(
        default=None, desc="A list of related issues or tasks, if any."
    )
    branch_name: str | None = dspy.InputField(
        default=None,
        desc="The current git branch name, used as extra context about the change's intent.",
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step reasoning about the commits and how they inform the title."
    )
    title: str = dspy.OutputField(
        desc="A single Conventional Commits v1.0.0 header line, for example 'feat(auth): add token refresh'."
    )
