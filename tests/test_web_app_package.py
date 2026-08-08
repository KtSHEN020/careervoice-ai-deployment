"""Deployment checks for the CareerVoice AI web application package."""

from importlib.metadata import version
from pathlib import Path
from shutil import which

from streamlit.testing.v1 import AppTest

import careervoice_ai_web_app


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "packages" / "careervoice-ai-web-app"


def test_web_app_package_is_importable() -> None:
    """The deployment environment should install the web application."""

    assert careervoice_ai_web_app.__version__ == "0.1.0"
    assert version("careervoice-ai-web-app") == "0.1.0"


def test_streamlit_command_is_installed() -> None:
    """Installing the web application should install Streamlit."""

    assert which("streamlit") is not None


def test_web_app_snapshot_excludes_unsafe_files() -> None:
    """The imported snapshot must not contain unsafe local files."""

    forbidden_paths = [
        PACKAGE_ROOT / ".env",
        PACKAGE_ROOT / ".git",
        PACKAGE_ROOT / ".venv",
        PACKAGE_ROOT / "uv.lock",
        PACKAGE_ROOT / "runtime",
    ]

    present_paths = [
        path.relative_to(ROOT)
        for path in forbidden_paths
        if path.exists()
    ]

    assert not present_paths, (
        f"Package snapshot contains forbidden paths: {present_paths}"
    )


def test_deployment_entrypoint_renders() -> None:
    """The deployment root entry point should launch the web interface."""

    app = AppTest.from_file(str(ROOT / "app.py")).run(
        timeout=15
    )

    assert len(app.exception) == 0
    assert app.title[0].value == "CareerVoice AI"