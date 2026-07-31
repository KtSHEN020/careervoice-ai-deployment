import json
from pathlib import Path

import pytest

from preference_aware_job_recommender.data_loader import (
    load_career_profile,
    load_jobs,
)


EXAMPLES_DIR = Path("examples")


def test_load_career_profile_from_example() -> None:
    profile = load_career_profile(EXAMPLES_DIR / "career_profile.json")

    assert isinstance(profile, dict)
    assert "skills" in profile
    assert "target_roles" in profile


def test_load_jobs_from_example() -> None:
    jobs = load_jobs(EXAMPLES_DIR / "jobs.json")

    assert isinstance(jobs, list)
    assert len(jobs) > 0
    assert "job_id" in jobs[0]
    assert "title" in jobs[0]


def test_load_career_profile_rejects_non_object_json(tmp_path: Path) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(json.dumps(["Python", "SQL"]), encoding="utf-8")

    with pytest.raises(ValueError, match="object"):
        load_career_profile(profile_path)


def test_load_jobs_rejects_non_list_json(tmp_path: Path) -> None:
    jobs_path = tmp_path / "jobs.json"
    jobs_path.write_text(json.dumps({"job_id": "job_001"}), encoding="utf-8")

    with pytest.raises(ValueError, match="list"):
        load_jobs(jobs_path)


def test_load_jobs_rejects_list_with_non_object_items(tmp_path: Path) -> None:
    jobs_path = tmp_path / "jobs.json"
    jobs_path.write_text(
        json.dumps(
            [
                {"job_id": "job_001", "title": "Junior Backend Developer"},
                "invalid job item",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Each job"):
        load_jobs(jobs_path)

def test_load_career_profile_reports_invalid_json(tmp_path: Path) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text('{"skills": ["Python",}', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_career_profile(profile_path)