from pydantic import ValidationError
import pytest

from job_listing_collector.models import NormalizedJob


def make_valid_job_data() -> dict:
    return {
        "job_id": "adzuna_001",
        "title": "Junior Backend Developer",
        "company": "Example Tech",
        "location": "Adelaide",
        "work_type": "hybrid",
        "seniority": "junior",
        "description": "Build and maintain backend services.",
        "required_skills": ["Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS"],
        "responsibilities": ["Develop backend features"],
        "tags": ["backend development", "software engineering"],
        "source": "adzuna",
        "source_url": "https://example.com/jobs/001",
        "collected_at": "2026-06-20T10:00:00Z",
    }


def test_can_create_normalized_job() -> None:
    job = NormalizedJob(**make_valid_job_data())

    assert job.job_id == "adzuna_001"
    assert job.title == "Junior Backend Developer"
    assert job.company == "Example Tech"
    assert job.location == "Adelaide"
    assert job.work_type == "hybrid"
    assert job.seniority == "junior"
    assert job.required_skills == ["Python", "SQL", "Git"]


def test_normalized_job_can_export_json_compatible_dict() -> None:
    job = NormalizedJob(**make_valid_job_data())

    exported = job.to_repo2_dict()

    assert exported["job_id"] == "adzuna_001"
    assert exported["title"] == "Junior Backend Developer"
    assert exported["source"] == "adzuna"
    assert exported["source_url"] == "https://example.com/jobs/001"
    assert isinstance(exported["collected_at"], str)


def test_required_string_fields_are_stripped() -> None:
    data = make_valid_job_data()
    data["title"] = "  Junior Backend Developer  "

    job = NormalizedJob(**data)

    assert job.title == "Junior Backend Developer"


def test_empty_required_string_is_rejected() -> None:
    data = make_valid_job_data()
    data["title"] = "   "

    with pytest.raises(ValidationError):
        NormalizedJob(**data)


def test_list_fields_are_cleaned() -> None:
    data = make_valid_job_data()
    data["required_skills"] = [" Python ", "", " SQL ", "Git"]

    job = NormalizedJob(**data)

    assert job.required_skills == ["Python", "SQL", "Git"]


def test_invalid_work_type_is_rejected() -> None:
    data = make_valid_job_data()
    data["work_type"] = "work from home"

    with pytest.raises(ValidationError):
        NormalizedJob(**data)


def test_invalid_seniority_is_rejected() -> None:
    data = make_valid_job_data()
    data["seniority"] = "entry level"

    with pytest.raises(ValidationError):
        NormalizedJob(**data)


def test_unexpected_extra_field_is_rejected() -> None:
    data = make_valid_job_data()
    data["salary"] = "$70,000"

    with pytest.raises(ValidationError):
        NormalizedJob(**data)