import json
from pathlib import Path

from job_listing_collector.models import NormalizedJob


def test_example_jobs_file_exists() -> None:
    path = Path("examples/example_jobs.json")

    assert path.exists()


def test_example_jobs_file_contains_valid_json_list() -> None:
    path = Path("examples/example_jobs.json")

    data = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert len(data) > 0


def test_example_jobs_match_normalized_job_schema() -> None:
    path = Path("examples/example_jobs.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    jobs = [NormalizedJob(**item) for item in data]

    assert len(jobs) == len(data)
    assert jobs[0].job_id == "example_001"
    assert jobs[0].title == "Junior Backend Developer"
    assert jobs[0].required_skills == ["Python", "SQL", "Git"]


def test_example_jobs_are_json_serializable_after_validation() -> None:
    path = Path("examples/example_jobs.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    jobs = [NormalizedJob(**item) for item in data]
    exported_jobs = [job.to_repo2_dict() for job in jobs]

    assert exported_jobs[0]["collected_at"] == "2026-06-20T10:00:00Z"