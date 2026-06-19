"""PR Summary generation service - business logic layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from usepr.modules.pull_request_summary_generator import (
    PullRequestSummaryGeneratorModule,
)
from usepr.utils.git import (
    ensure_git_repo,
    get_commits_between,
    get_default_branch,
    parse_commits,
    resolve_ref,
)
from usepr.utils.github import PrTemplate, find_pr_templates


@dataclass
class SummaryResult:
    """Result from PR summary generation."""

    reasoning: str
    summary: str


@dataclass
class CommitContext:
    """Context about commits for summary generation."""

    commits: list[str]
    base_branch: str
    default_branch: str


def get_default_branch_name(repo_path: str) -> str:
    """Get the default branch name for the repository.

    Args:
        repo_path: Absolute path to the repository.

    Returns:
        The default branch name (e.g., 'main' or 'master').
    """
    return get_default_branch(repo_path).strip()


def gather_commits(repo_path: str, base_branch: str) -> CommitContext:
    """Gather commits between base branch and HEAD.

    Args:
        repo_path: Absolute path to the repository.
        base_branch: The base branch to diff against.

    Returns:
        CommitContext with parsed commits and branch info.

    Raises:
        SystemExit: If not a git repository or ref cannot be resolved.
    """
    ensure_git_repo(repo_path)

    default_branch = get_default_branch_name(repo_path)
    prev_tag = resolve_ref(repo_path, base_branch)

    commit_text = get_commits_between(repo_path, prev_tag, "HEAD")
    commits = parse_commits(commit_text)

    return CommitContext(
        commits=commits,
        base_branch=base_branch,
        default_branch=default_branch,
    )


def generate_summary(
    commits: list[str],
    related_issues: Optional[str] = None,
    template: Optional[str] = None,
) -> SummaryResult:
    """Generate a PR summary from commits.

    Args:
        commits: List of commit messages.
        related_issues: Optional comma-separated related issues.
        template: Optional PR template content.

    Returns:
        SummaryResult with reasoning and summary.
    """
    program = PullRequestSummaryGeneratorModule()
    result = program(
        commits=commits,
        related_issues=related_issues,
        template=template,
    )

    return SummaryResult(
        reasoning=result.reasoning,
        summary=result.summary,
    )


def get_templates(repo_path: str) -> list[PrTemplate]:
    """Find PR templates in the repository.

    Args:
        repo_path: Absolute path to the repository.

    Returns:
        List of found PR templates.
    """
    return find_pr_templates(repo_path)
