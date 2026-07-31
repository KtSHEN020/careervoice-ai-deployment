import json
from pathlib import Path


EXAMPLES_DIR = Path("examples")


def test_career_profile_sample_is_valid_json() -> None:
    profile_path = EXAMPLES_DIR / "career_profile.json"

    with profile_path.open(encoding="utf-8") as file:
        profile = json.load(file)

    assert isinstance(profile, dict)


def test_career_profile_sample_has_minimum_required_fields() -> None:
    profile_path = EXAMPLES_DIR / "career_profile.json"

    with profile_path.open(encoding="utf-8") as file:
        profile = json.load(file)

    minimum_required_fields = {
        "target_roles",
        "skills",
        "experience_level",
    }

    assert minimum_required_fields.issubset(profile.keys())


def test_jobs_sample_is_valid_json_list() -> None:
    jobs_path = EXAMPLES_DIR / "jobs.json"

    with jobs_path.open(encoding="utf-8") as file:
        jobs = json.load(file)

    assert isinstance(jobs, list)
    assert len(jobs) > 0


def test_jobs_sample_has_minimum_required_fields() -> None:
    jobs_path = EXAMPLES_DIR / "jobs.json"

    with jobs_path.open(encoding="utf-8") as file:
        jobs = json.load(file)

    minimum_required_fields = {
        "job_id",
        "title",
        "company",
        "required_skills",
    }

    for job in jobs:
        assert minimum_required_fields.issubset(job.keys())


def test_sample_job_ids_are_unique() -> None:
    jobs_path = EXAMPLES_DIR / "jobs.json"

    with jobs_path.open(encoding="utf-8") as file:
        jobs = json.load(file)

    job_ids = [job["job_id"] for job in jobs]

    assert len(job_ids) == len(set(job_ids))