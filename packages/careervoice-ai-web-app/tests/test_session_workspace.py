from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from careervoice_ai_web_app.session_workspace import SessionWorkspace


def test_create_workspace_uses_unique_session_id(
    tmp_path: Path,
) -> None:
    root_dir = tmp_path / "runtime" / "sessions"

    first_workspace = SessionWorkspace.create(root_dir=root_dir)
    second_workspace = SessionWorkspace.create(root_dir=root_dir)

    assert first_workspace.session_id != second_workspace.session_id
    assert UUID(first_workspace.session_id)
    assert UUID(second_workspace.session_id)
    assert first_workspace.directory.is_dir()
    assert second_workspace.directory.is_dir()


def test_workspace_exposes_session_specific_file_paths(
    tmp_path: Path,
) -> None:
    workspace = SessionWorkspace.create(root_dir=tmp_path)

    assert workspace.profile_input_path == (
        workspace.directory / "profile_input.txt"
    )
    assert workspace.profile_path == (
        workspace.directory / "career_profile.json"
    )
    assert workspace.jobs_output_path == workspace.directory / "jobs.json"
    assert workspace.recommendations_output_path == (
        workspace.directory / "recommendations.json"
    )


def test_generated_paths_contains_all_workflow_files(
    tmp_path: Path,
) -> None:
    workspace = SessionWorkspace.create(root_dir=tmp_path)

    assert workspace.generated_paths == (
        workspace.profile_input_path,
        workspace.profile_path,
        workspace.jobs_output_path,
        workspace.recommendations_output_path,
    )


def test_existing_session_id_reopens_same_workspace(
    tmp_path: Path,
) -> None:
    original_workspace = SessionWorkspace.create(root_dir=tmp_path)
    original_workspace.profile_input_path.write_text(
        "Existing career preference text",
        encoding="utf-8",
    )

    reopened_workspace = SessionWorkspace.from_session_id(
        original_workspace.session_id,
        root_dir=tmp_path,
    )

    assert reopened_workspace.directory == original_workspace.directory
    assert reopened_workspace.profile_input_path.read_text(
        encoding="utf-8"
    ) == "Existing career preference text"


@pytest.mark.parametrize(
    "invalid_session_id",
    [
        "",
        "not-a-uuid",
        "../another-directory",
        "../../outside-runtime",
    ],
)
def test_invalid_session_id_is_rejected(
    invalid_session_id: str,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="valid UUID"):
        SessionWorkspace(
            session_id=invalid_session_id,
            root_dir=tmp_path,
        )


def test_clear_removes_only_selected_workspace(
    tmp_path: Path,
) -> None:
    first_workspace = SessionWorkspace.create(root_dir=tmp_path)
    second_workspace = SessionWorkspace.create(root_dir=tmp_path)

    first_workspace.profile_path.write_text("{}", encoding="utf-8")
    second_workspace.profile_path.write_text("{}", encoding="utf-8")

    first_workspace.clear()

    assert not first_workspace.directory.exists()
    assert second_workspace.directory.exists()
    assert second_workspace.profile_path.exists()