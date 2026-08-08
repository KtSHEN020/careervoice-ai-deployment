"""Shared pytest configuration for the job collector tests."""

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def run_tests_from_project_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve repository-relative test paths from the project root."""

    monkeypatch.chdir(PROJECT_ROOT)