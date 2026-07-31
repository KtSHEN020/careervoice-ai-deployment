"""Tests for the initial deployment repository structure."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_deployment_paths_exist() -> None:
    """The deployment repository should contain its required root structure."""

    required_paths = [
        "app.py",
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "packages",
        "scripts",
        "docs",
        "tests",
        ".streamlit",
    ]

    missing_paths = [
        relative_path
        for relative_path in required_paths
        if not (ROOT / relative_path).exists()
    ]

    assert not missing_paths, (
        f"Missing required deployment paths: {missing_paths}"
    )


def test_sensitive_local_files_are_absent() -> None:
    """Sensitive local configuration must not exist in tracked locations."""

    sensitive_paths = [
        ".env",
        ".streamlit/secrets.toml",
    ]

    present_paths = [
        relative_path
        for relative_path in sensitive_paths
        if (ROOT / relative_path).exists()
    ]

    assert not present_paths, (
        f"Sensitive local files must not be committed: {present_paths}"
    )