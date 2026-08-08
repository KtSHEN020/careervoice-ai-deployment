from datetime import datetime, timezone

from job_listing_collector.normalizer import (
    build_job_id,
    clean_description,
    extract_responsibilities,
    extract_skills,
    infer_seniority,
    infer_tags,
    infer_work_type,
    normalize_raw_job,
    normalize_raw_jobs,
)
from job_listing_collector.sources import RawJobRecord


def make_raw_job() -> RawJobRecord:
    return RawJobRecord(
        source="adzuna",
        source_job_id="123",
        title="Junior Backend Developer",
        company="Example Tech",
        location="Adelaide SA",
        description=(
            "<p>Build and maintain backend APIs using Python, SQL, and Git.</p> "
            "Docker is preferred. Collaborate with the software team."
        ),
        source_url="https://www.adzuna.com.au/jobs/details/123",
        raw_data={"category": "IT Jobs"},
    )


def test_normalize_raw_job_returns_normalized_job() -> None:
    collected_at = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)

    job = normalize_raw_job(make_raw_job(), collected_at=collected_at)

    assert job.job_id == "adzuna_123"
    assert job.title == "Junior Backend Developer"
    assert job.company == "Example Tech"
    assert job.location == "Adelaide SA"
    assert job.work_type == "unknown"
    assert job.seniority == "junior"
    assert job.description == (
        "Build and maintain backend APIs using Python, SQL, and Git. "
        "Docker is preferred. Collaborate with the software team."
    )
    assert job.required_skills == ["Python", "SQL", "Git"]
    assert job.preferred_skills == ["Docker"]
    assert job.responsibilities == [
        "Build and maintain backend APIs using Python, SQL, and Git.",
        "Collaborate with the software team.",
    ]
    assert job.tags == ["backend development", "data", "devops", "software engineering"]
    assert job.source == "adzuna"
    assert job.source_url == "https://www.adzuna.com.au/jobs/details/123"
    assert job.collected_at == collected_at


def test_normalize_raw_jobs_returns_multiple_normalized_jobs() -> None:
    collected_at = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)

    jobs = normalize_raw_jobs(
        [make_raw_job(), make_raw_job()],
        collected_at=collected_at,
    )

    assert len(jobs) == 2
    assert jobs[0].job_id == "adzuna_123"
    assert jobs[1].job_id == "adzuna_123"


def test_build_job_id_sanitizes_source_and_source_job_id() -> None:
    raw_job = RawJobRecord(
        source="Adzuna Source",
        source_job_id="Job 123/ABC",
        title="Developer",
        company="Example Tech",
        location="Adelaide",
        description="Build software.",
        source_url="https://example.com/jobs/123",
    )

    assert build_job_id(raw_job) == "adzuna_source_job_123_abc"


def test_clean_description_removes_html_and_normalizes_whitespace() -> None:
    description = "<p>Build APIs&nbsp;with Python.</p>\n<p>Use SQL.</p>"

    assert clean_description(description) == "Build APIs with Python. Use SQL."


def test_infer_work_type_detects_hybrid() -> None:
    assert infer_work_type("This is a hybrid role in Adelaide.") == "hybrid"


def test_infer_work_type_detects_remote() -> None:
    assert infer_work_type("This role supports remote work.") == "remote"


def test_infer_work_type_detects_onsite() -> None:
    assert infer_work_type("This is an on-site office based role.") == "onsite"


def test_infer_work_type_returns_unknown_when_not_found() -> None:
    assert infer_work_type("This is a software developer role.") == "unknown"


def test_infer_seniority_detects_intern() -> None:
    assert infer_seniority("Software Engineering Internship") == "intern"


def test_infer_seniority_detects_junior() -> None:
    assert infer_seniority("Graduate Junior Developer") == "junior"


def test_infer_seniority_detects_mid() -> None:
    assert infer_seniority("Mid-level Python Developer") == "mid"


def test_infer_seniority_detects_senior() -> None:
    assert infer_seniority("Senior Backend Engineer") == "senior"


def test_infer_seniority_detects_lead() -> None:
    assert infer_seniority("Lead Software Engineer") == "lead"


def test_extract_skills_splits_required_and_preferred_skills() -> None:
    text = "Use Python, SQL, and Git. Docker and AWS are preferred."

    required_skills, preferred_skills = extract_skills(text)

    assert required_skills == ["Python", "SQL", "Git"]
    assert preferred_skills == ["Docker", "AWS"]


def test_extract_responsibilities_returns_matching_sentences() -> None:
    description = (
        "Build backend services. "
        "Free snacks are available. "
        "Collaborate with product teams."
    )

    responsibilities = extract_responsibilities(description)

    assert responsibilities == [
        "Build backend services.",
        "Collaborate with product teams.",
    ]


def test_extract_responsibilities_falls_back_to_first_sentence() -> None:
    description = "This is a friendly team. Great office."

    responsibilities = extract_responsibilities(description)

    assert responsibilities == ["This is a friendly team."]


def test_infer_tags_returns_general_when_no_specific_tags_found() -> None:
    tags = infer_tags("Friendly workplace.", skills=[])

    assert tags == ["general"]


def test_infer_tags_detects_software_engineering_from_skills() -> None:
    tags = infer_tags("Build backend services on AWS.", skills=["Python"])

    assert tags == [
        "backend development",
        "cloud",
        "software engineering",
    ]

def test_normalize_raw_job_uses_title_seniority_before_description() -> None:
    raw_job = RawJobRecord(
        source="adzuna",
        source_job_id="456",
        title="Senior Developer",
        company="Example Tech",
        location="Adelaide",
        description="Lead delivery of software projects with internal teams.",
        source_url="https://example.com/jobs/456",
    )

    job = normalize_raw_job(raw_job)

    assert job.seniority == "senior"


def test_infer_tags_detects_software_engineering_from_job_title() -> None:
    tags = infer_tags("Software Developer", skills=[])

    assert tags == ["software engineering"]