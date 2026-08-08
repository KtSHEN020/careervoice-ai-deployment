from __future__ import annotations

from pathlib import Path

from careervoice_ai_web_app import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_package_version() -> None:
    assert __version__ == "0.1.0"


def test_required_project_files_exist() -> None:
    required_paths = [
        PROJECT_ROOT / "app.py",
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / ".gitignore",
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "web.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "errors.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "models.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "orchestrator_gateway.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "runtime_check.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "session_workspace.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "ui_state.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "workflow_service.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "recommendation_models.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "recommendation_ui.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "document_input.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "scanned_document.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "document_recognition.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "voice_input.py",
        PROJECT_ROOT
        / "src"
        / "careervoice_ai_web_app"
        / "voice_transcription.py",
    ]

    for path in required_paths:
        assert path.exists(), (
            f"Required project file is missing: {path}"
        )