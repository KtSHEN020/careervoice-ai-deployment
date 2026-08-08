import json
from datetime import datetime, timezone

from job_listing_collector.exporter import export_jobs
from job_listing_collector.models import NormalizedJob


def make_job(
    *,
    job_id: str = "adzuna_123",
    title: str = "Junior Backend Developer",
) -> NormalizedJob:
    return NormalizedJob(
        job_id=job_id,
        title=title,
        company="Example Tech",
        location="Adelaide SA",
        work_type="hybrid",
        seniority="junior",
        description="Build and maintain backend services.",
        required_skills=["Python", "SQL"],
        preferred_skills=["Docker"],
        responsibilities=["Build backend features."],
        tags=["backend development", "software engineering"],
        source="adzuna",
        source_url="https://www.adzuna.com.au/jobs/details/123",
        collected_at=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
    )


def test_export_jobs_creates_json_file(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"

    returned_path = export_jobs([make_job()], output_path)

    assert returned_path == output_path
    assert output_path.exists()


def test_export_jobs_writes_list_of_jobs(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"

    export_jobs(
        [
            make_job(job_id="adzuna_123"),
            make_job(job_id="adzuna_456", title="Frontend Developer"),
        ],
        output_path,
    )

    exported_data = json.loads(output_path.read_text(encoding="utf-8"))

    assert isinstance(exported_data, list)
    assert len(exported_data) == 2
    assert exported_data[0]["job_id"] == "adzuna_123"
    assert exported_data[1]["job_id"] == "adzuna_456"


def test_export_jobs_writes_repo2_compatible_fields(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"

    export_jobs([make_job()], output_path)

    exported_job = json.loads(output_path.read_text(encoding="utf-8"))[0]

    assert exported_job == {
        "job_id": "adzuna_123",
        "title": "Junior Backend Developer",
        "company": "Example Tech",
        "location": "Adelaide SA",
        "work_type": "hybrid",
        "seniority": "junior",
        "description": "Build and maintain backend services.",
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Docker"],
        "responsibilities": ["Build backend features."],
        "tags": ["backend development", "software engineering"],
        "source": "adzuna",
        "source_url": "https://www.adzuna.com.au/jobs/details/123",
        "collected_at": "2026-06-20T10:00:00Z",
    }


def test_export_jobs_creates_parent_directory(tmp_path) -> None:
    output_path = tmp_path / "outputs" / "jobs.json"

    export_jobs([make_job()], output_path)

    assert output_path.exists()


def test_export_jobs_can_export_empty_list(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"

    export_jobs([], output_path)

    exported_data = json.loads(output_path.read_text(encoding="utf-8"))

    assert exported_data == []


def test_export_jobs_overwrites_existing_file(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"
    output_path.write_text("old content", encoding="utf-8")

    export_jobs([make_job()], output_path)

    exported_data = json.loads(output_path.read_text(encoding="utf-8"))

    assert exported_data[0]["job_id"] == "adzuna_123"


def test_export_jobs_preserves_non_ascii_text(tmp_path) -> None:
    output_path = tmp_path / "jobs.json"
    job = make_job(title="Développeur Backend Junior")

    export_jobs([job], output_path)

    exported_text = output_path.read_text(encoding="utf-8")

    assert "Développeur Backend Junior" in exported_text