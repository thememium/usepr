"""Utilities for detecting and reading GitHub PR templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PrTemplate:
    """A detected PR template."""

    path: str
    content: str
    name: Optional[str] = None


TEMPLATE_FILENAMES = ["PULL_REQUEST_TEMPLATE.md"]

TEMPLATE_DIR_NAME = "PULL_REQUEST_TEMPLATE"

GITHUB_DIR = ".github"


def _read_text(path: Path) -> Optional[str]:
    """Read a text file, returning None if unreadable."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def find_pr_templates(repo_path: str) -> List[PrTemplate]:
    """
    Find all PR templates in the repository.

    Searches the following locations in order:
      1. .github/PULL_REQUEST_TEMPLATE.md
      2. .github/PULL_REQUEST_TEMPLATE/*.md (all .md files in the directory)
      3. PULL_REQUEST_TEMPLATE.md (repo root)

    Args:
        repo_path: Absolute path to the repository root.

    Returns:
        List of PrTemplate objects found. Empty list if none found.
    """
    root = Path(repo_path)
    templates: List[PrTemplate] = []

    # 1. .github/PULL_REQUEST_TEMPLATE.md
    github_dir = root / GITHUB_DIR
    for filename in TEMPLATE_FILENAMES:
        candidate = github_dir / filename
        content = _read_text(candidate)
        if content:
            templates.append(
                PrTemplate(path=str(candidate), content=content, name=None)
            )

    # 2. .github/PULL_REQUEST_TEMPLATE/*.md
    template_dir = github_dir / TEMPLATE_DIR_NAME
    if template_dir.is_dir():
        for md_file in sorted(template_dir.glob("*.md")):
            content = _read_text(md_file)
            if content:
                templates.append(
                    PrTemplate(
                        path=str(md_file),
                        content=content,
                        name=md_file.stem,
                    )
                )

    # 3. Root-level PULL_REQUEST_TEMPLATE.md
    for filename in TEMPLATE_FILENAMES:
        candidate = root / filename
        content = _read_text(candidate)
        if content:
            templates.append(
                PrTemplate(path=str(candidate), content=content, name=None)
            )

    return templates
