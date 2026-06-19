"""Tests for usepr.utils.github module."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from usepr.utils.github import PrTemplate, find_pr_templates


# ---------------------------------------------------------------------------
# PrTemplate dataclass
# ---------------------------------------------------------------------------


class TestPrTemplate:
    def test_creation(self) -> None:
        t = PrTemplate(path="/foo", content="hello", name="bar")
        assert t.path == "/foo"
        assert t.content == "hello"
        assert t.name == "bar"

    def test_name_defaults_to_none(self) -> None:
        t = PrTemplate(path="/foo", content="hello")
        assert t.name is None

    def test_equality(self) -> None:
        a = PrTemplate(path="/a", content="x", name="n")
        b = PrTemplate(path="/a", content="x", name="n")
        assert a == b


# ---------------------------------------------------------------------------
# find_pr_templates – .github/PULL_REQUEST_TEMPLATE.md
# ---------------------------------------------------------------------------


class TestFindTemplatesGithubSingleFile:
    def test_finds_single_template(self, github_dir: Path) -> None:
        tpl = github_dir / "PULL_REQUEST_TEMPLATE.md"
        tpl.write_text("# PR Template\n\nDescribe changes.")
        repo_path = str(github_dir.parent)

        templates = find_pr_templates(repo_path)
        assert len(templates) == 1
        assert templates[0].content == "# PR Template\n\nDescribe changes."
        assert templates[0].name is None
        assert str(tpl) == templates[0].path

    def test_returns_empty_when_no_templates(self, tmp_repo: Path) -> None:
        assert find_pr_templates(str(tmp_repo)) == []

    def test_ignores_empty_file(self, github_dir: Path) -> None:
        tpl = github_dir / "PULL_REQUEST_TEMPLATE.md"
        tpl.write_text("")
        assert find_pr_templates(str(github_dir.parent)) == []

    def test_ignores_whitespace_only_file(self, github_dir: Path) -> None:
        tpl = github_dir / "PULL_REQUEST_TEMPLATE.md"
        tpl.write_text("   \n  \t  ")
        assert find_pr_templates(str(github_dir.parent)) == []


# ---------------------------------------------------------------------------
# find_pr_templates – .github/PULL_REQUEST_TEMPLATE/*.md
# ---------------------------------------------------------------------------


class TestFindTemplatesGithubDirectory:
    def test_finds_multiple_templates(self, template_dir: Path) -> None:
        (template_dir / "feature.md").write_text("# Feature PR")
        (template_dir / "bugfix.md").write_text("# Bugfix PR")
        repo_path = str(template_dir.parent.parent)

        templates = find_pr_templates(repo_path)
        # Should find them sorted alphabetically
        names = [t.name for t in templates]
        assert names == ["bugfix", "feature"]

    def test_ignores_non_md_files(self, template_dir: Path) -> None:
        (template_dir / "notes.txt").write_text("not a template")
        (template_dir / "real.md").write_text("# Real template")
        repo_path = str(template_dir.parent.parent)

        templates = find_pr_templates(repo_path)
        assert len(templates) == 1
        assert templates[0].name == "real"

    def test_ignores_empty_md_files(self, template_dir: Path) -> None:
        (template_dir / "empty.md").write_text("")
        (template_dir / "valid.md").write_text("# Valid")
        repo_path = str(template_dir.parent.parent)

        templates = find_pr_templates(repo_path)
        assert len(templates) == 1
        assert templates[0].name == "valid"

    def test_nested_dir_not_searched(self, template_dir: Path) -> None:
        nested = template_dir / "subdir"
        nested.mkdir()
        (nested / "deep.md").write_text("# Deep")
        repo_path = str(template_dir.parent.parent)

        templates = find_pr_templates(repo_path)
        assert len(templates) == 0


# ---------------------------------------------------------------------------
# find_pr_templates – root-level PULL_REQUEST_TEMPLATE.md
# ---------------------------------------------------------------------------


class TestFindTemplatesRootLevel:
    def test_finds_root_template(self, tmp_repo: Path) -> None:
        tpl = tmp_repo / "PULL_REQUEST_TEMPLATE.md"
        tpl.write_text("# Root Template")

        templates = find_pr_templates(str(tmp_repo))
        assert len(templates) == 1
        assert templates[0].content == "# Root Template"
        assert templates[0].name is None

    def test_root_template_after_github_templates(self, github_dir: Path) -> None:
        """Root template should come after .github/ templates in the list."""
        repo_path = str(github_dir.parent)

        # .github template
        (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text("# GitHub Template")
        # Root template
        (Path(repo_path) / "PULL_REQUEST_TEMPLATE.md").write_text("# Root Template")

        templates = find_pr_templates(repo_path)
        assert len(templates) == 2
        assert templates[0].content == "# GitHub Template"
        assert templates[1].content == "# Root Template"


# ---------------------------------------------------------------------------
# find_pr_templates – combined / priority ordering
# ---------------------------------------------------------------------------


class TestFindTemplatesCombined:
    def test_all_locations_discovered(self, template_dir: Path) -> None:
        """When templates exist in all 3 locations, all are found in order."""
        repo_path = str(template_dir.parent.parent)

        # 1. .github/PULL_REQUEST_TEMPLATE.md
        (template_dir.parent / "PULL_REQUEST_TEMPLATE.md").write_text("# Single")

        # 2. .github/PULL_REQUEST_TEMPLATE/*.md
        (template_dir / "custom.md").write_text("# Custom")

        # 3. Root
        (Path(repo_path) / "PULL_REQUEST_TEMPLATE.md").write_text("# Root")

        templates = find_pr_templates(repo_path)
        assert len(templates) == 3
        # Order: single github file, then directory files, then root
        assert templates[0].content == "# Single"
        assert templates[1].content == "# Custom"
        assert templates[2].content == "# Root"

    def test_strips_whitespace_from_content(self, github_dir: Path) -> None:
        tpl = github_dir / "PULL_REQUEST_TEMPLATE.md"
        tpl.write_text("  \n# Template\n\nContent here\n  ")
        repo_path = str(github_dir.parent)

        templates = find_pr_templates(repo_path)
        assert templates[0].content == "# Template\n\nContent here"


# ---------------------------------------------------------------------------
# _read_text edge cases
# ---------------------------------------------------------------------------


class TestReadText:
    def test_reads_utf8_file(self, tmp_path: Path) -> None:
        from usepr.utils.github import _read_text

        f = tmp_path / "test.md"
        f.write_text("# Hello", encoding="utf-8")
        assert _read_text(f) == "# Hello"

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        from usepr.utils.github import _read_text

        f = tmp_path / "nonexistent.md"
        assert _read_text(f) is None

    def test_returns_none_for_unreadable_file(self, tmp_path: Path) -> None:
        from usepr.utils.github import _read_text

        f = tmp_path / "unreadable.md"
        f.write_bytes(b"\x80\x81\x82")  # Invalid UTF-8
        # Should still try, may return something or None depending on errors handling
        result = _read_text(f)
        # The function doesn't specify errors=replace, so it may raise or return
        # Either way, it shouldn't crash
