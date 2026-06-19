import subprocess
import sys
from typing import List, Optional

from usecli import console


def run(cmd: list[str], cwd: Optional[str] = None) -> str:
    """
    Run a command and return its output as a string.

    Args:
        cmd: List of command arguments.
        cwd: Optional working directory.

    Returns:
        The command output as a string.
    """
    return (
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=cwd)
        .decode("utf-8", errors="replace")
        .strip()
    )


def ensure_git_repo(repo_path: str) -> None:
    """
    Ensure the given path is a git repository.

    Args:
        repo_path: Path to the repository.

    Raises:
        SystemExit: If not a git repository.
    """
    try:
        run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_path)
    except subprocess.CalledProcessError:
        sys.stderr.write(f"[error] Not a git repository: {repo_path}\n")
        sys.exit(2)


def get_commits_between(
    repo_path: str, prev_tag: Optional[str], latest_tag: str = "HEAD"
) -> str:
    """
    Get commit messages between two tags.

    Args:
        repo_path: Path to the repository.
        prev_tag: Previous tag, or None to use default branch.
        latest_tag: Latest tag.

    Returns:
        Formatted commit messages as string.
    """
    # Format: subject, newline, newline, body, separator
    fmt = "%s%n%n%b----"
    if prev_tag is None:
        prev_tag = get_default_branch(repo_path)
    rng = f"{prev_tag}..{latest_tag}"
    result = subprocess.run(
        ["git", "log", "--no-merges", f"--format={fmt}", rng],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    text = result.stdout.strip()
    # Remove trailing separator
    if text.endswith("----"):
        text = text[:-4].rstrip()
    return text


def get_default_branch(repo_path: str) -> str:
    """Get the default branch of the repository (main or master)."""
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("/")[-1]
    except subprocess.CalledProcessError:
        # Fallback: check if 'main' exists, else 'master'
        try:
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", "refs/heads/main"],
                cwd=repo_path,
                check=True,
            )
            return "main"
        except subprocess.CalledProcessError:
            return "master"


def resolve_ref(repo_path: str, ref: str) -> str:
    """Resolve a ref, trying the bare name first then origin/<ref>."""
    for candidate in [ref, f"origin/{ref}"]:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", candidate],
            cwd=repo_path,
            capture_output=True,
        )
        if result.returncode == 0:
            return candidate
    console.print(
        f"[bold red]Error: Could not resolve ref '{ref}'. Make sure the branch exists locally or on the remote.[/bold red]"
    )
    sys.exit(1)


def parse_commits(commit_text: str) -> List[str]:
    """
    Parse the commit output into a list of individual commit messages.

    Args:
        commit_text: The formatted commit messages string from get_commits_between.

    Returns:
        List of individual commit messages.
    """
    return [commit.strip() for commit in commit_text.split("----") if commit.strip()]
