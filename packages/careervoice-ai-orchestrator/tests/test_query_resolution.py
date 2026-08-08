from pathlib import Path

import pytest

from careervoice_ai_orchestrator.models import WorkflowConfig
from careervoice_ai_orchestrator.query_resolution import (
    extract_target_roles,
    load_career_profile,
    resolve_job_queries,
)


def test_load_career_profile_returns_json_object(tmp_path: Path) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": ["software developer"]}',
        encoding="utf-8",
    )

    profile_data = load_career_profile(profile_path)

    assert profile_data == {
        "target_roles": ["software developer"],
    }


def test_load_career_profile_rejects_missing_file(tmp_path: Path) -> None:
    profile_path = tmp_path / "missing_profile.json"

    with pytest.raises(ValueError, match="Career profile file was not found"):
        load_career_profile(profile_path)


def test_load_career_profile_rejects_invalid_json(tmp_path: Path) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": ["software developer"]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="contains invalid JSON"):
        load_career_profile(profile_path)


def test_load_career_profile_rejects_non_object_json(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '["software developer", "backend developer"]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must contain a JSON object"):
        load_career_profile(profile_path)


def test_extract_target_roles_returns_empty_tuple_when_field_is_missing() -> None:
    assert extract_target_roles({}) == ()


def test_extract_target_roles_cleans_and_deduplicates_roles() -> None:
    profile_data: dict[str, object] = {
        "target_roles": [
            " software developer ",
            "backend developer",
            "Software Developer",
            "",
            "   ",
            "data analyst",
            "BACKEND DEVELOPER",
        ]
    }

    target_roles = extract_target_roles(profile_data)

    assert target_roles == (
        "software developer",
        "backend developer",
        "data analyst",
    )


def test_extract_target_roles_rejects_non_list_value() -> None:
    profile_data: dict[str, object] = {
        "target_roles": "software developer",
    }

    with pytest.raises(
        ValueError,
        match="target_roles.*must be a list of strings",
    ):
        extract_target_roles(profile_data)


def test_extract_target_roles_rejects_non_string_items() -> None:
    profile_data: dict[str, object] = {
        "target_roles": [
            "software developer",
            123,
        ]
    }

    with pytest.raises(
        ValueError,
        match="target_roles.*must contain only strings",
    ):
        extract_target_roles(profile_data)


def test_resolve_job_queries_prefers_explicit_queries(
    tmp_path: Path,
) -> None:
    config = WorkflowConfig(
        profile_path=tmp_path / "missing_profile.json",
        job_queries=(
            "software developer",
            "backend developer",
        ),
    )

    queries = resolve_job_queries(config)

    assert queries == (
        "software developer",
        "backend developer",
    )


def test_resolve_job_queries_reads_target_roles_from_profile(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        """
        {
          "target_roles": [
            "software developer",
            "backend developer",
            "data analyst"
          ]
        }
        """,
        encoding="utf-8",
    )

    config = WorkflowConfig(
        profile_path=profile_path,
        job_queries=(),
    )

    queries = resolve_job_queries(config)

    assert queries == (
        "software developer",
        "backend developer",
        "data analyst",
    )


def test_resolve_job_queries_rejects_missing_queries_and_target_roles(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": []}',
        encoding="utf-8",
    )

    config = WorkflowConfig(
        profile_path=profile_path,
        job_queries=(),
    )

    with pytest.raises(
        ValueError,
        match="No job search queries were provided",
    ):
        resolve_job_queries(config)
