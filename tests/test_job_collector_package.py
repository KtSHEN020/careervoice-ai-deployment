"""Deployment checks for the job collector package."""

from importlib.metadata import version
from pathlib import Path
from shutil import which

import job_listing_collector


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "packages" / "job-listing-collector"


def test_job_collector_package_is_importable() -> None:
    """The deployment environment should install the imported package."""

    assert job_listing_collector.__version__ == "0.1.0"
    assert version("job-listing-collector") == "0.1.0"


def test_job_collector_command_is_installed() -> None:
    """Installing the package should create its command-line entry point."""

    assert which("job-collect") is not None


def test_job_collector_snapshot_excludes_unsafe_files() -> None:
    """The imported snapshot must not contain unsafe repository files."""

    forbidden_paths = [
        PACKAGE_ROOT / ".env",
        PACKAGE_ROOT / ".git",
        PACKAGE_ROOT / ".venv",
        PACKAGE_ROOT / "uv.lock",
    ]

    present_paths = [
        path.relative_to(ROOT)
        for path in forbidden_paths
        if path.exists()
    ]

    assert not present_paths, (
        f"Package snapshot contains forbidden paths: {present_paths}"
    )