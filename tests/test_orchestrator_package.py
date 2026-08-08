"""Deployment checks for the workflow coordinator package."""

from importlib.metadata import version
from pathlib import Path
from shutil import which

import careervoice_ai_orchestrator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "packages" / "careervoice-ai-orchestrator"


def test_orchestrator_package_is_importable() -> None:
    """The deployment environment should install the imported package."""

    assert careervoice_ai_orchestrator.__version__ == "0.1.0"
    assert version("careervoice-ai-orchestrator") == "0.1.0"


def test_orchestrator_command_is_installed() -> None:
    """Installing the package should create its command-line entry point."""

    assert which("careervoice-run") is not None


def test_orchestrator_snapshot_excludes_unsafe_files() -> None:
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