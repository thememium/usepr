"""Shared fixtures for usepr tests."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a temporary directory to act as a repo root."""
    return tmp_path


@pytest.fixture
def github_dir(tmp_repo: Path) -> Path:
    """Create .github directory inside tmp_repo."""
    d = tmp_repo / ".github"
    d.mkdir()
    return d


@pytest.fixture
def template_dir(github_dir: Path) -> Path:
    """Create .github/PULL_REQUEST_TEMPLATE directory."""
    d = github_dir / "PULL_REQUEST_TEMPLATE"
    d.mkdir()
    return d


@pytest.fixture
def mock_subprocess_run(monkeypatch: pytest.MonkeyPatch) -> Generator:
    """Patch subprocess.run for git command testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    monkeypatch.setattr("subprocess.run", mock)
    yield mock


@pytest.fixture
def mock_subprocess_check_output(monkeypatch: pytest.MonkeyPatch) -> Generator:
    """Patch subprocess.check_output for git command testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    monkeypatch.setattr("subprocess.check_output", mock)
    yield mock
