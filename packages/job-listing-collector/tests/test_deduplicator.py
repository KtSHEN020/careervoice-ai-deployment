from datetime import datetime, timezone

from job_listing_collector.deduplicator import (
    build_deduplication_key,
    deduplicate_jobs,
    normalize_key_part,
)
from job_listing_collector.models import NormalizedJob


def make_job(
    *,
    job_id: str = "adzuna_123",
    title: str = "Junior Backend Developer",
    company: str = "Example Tech",
    location: str = "Adelaide SA",
    source_url: str = "https://www.adzuna.com.au/jobs/details/123",
) -> NormalizedJob:
    return NormalizedJob(
        job_id=job_id,
        title=title,
        company=company,
        location=location,
        work_type="hybrid",
        seniority="junior",
        description="Build and maintain backend services.",
        required_skills=["Python", "SQL"],
        preferred_skills=["Docker"],
        responsibilities=["Build backend features."],
        tags=["backend development", "software engineering"],
        source="adzuna",
        source_url=source_url,
        collected_at=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
    )


def test_deduplicate_jobs_keeps_unique_jobs() -> None:
    jobs = [
        make_job(job_id="adzuna_123"),
        make_job(
            job_id="adzuna_456",
            title="Frontend Developer",
            source_url="https://www.adzuna.com.au/jobs/details/456",
        ),
    ]

    unique_jobs = deduplicate_jobs(jobs)

    assert len(unique_jobs) == 2
    assert unique_jobs[0].job_id == "adzuna_123"
    assert unique_jobs[1].job_id == "adzuna_456"


def test_deduplicate_jobs_removes_duplicate_source_urls() -> None:
    jobs = [
        make_job(job_id="adzuna_123"),
        make_job(job_id="adzuna_duplicate"),
    ]

    unique_jobs = deduplicate_jobs(jobs)

    assert len(unique_jobs) == 1
    assert unique_jobs[0].job_id == "adzuna_123"


def test_deduplicate_jobs_preserves_first_occurrence() -> None:
    jobs = [
        make_job(job_id="first"),
        make_job(job_id="second"),
        make_job(job_id="third"),
    ]

    unique_jobs = deduplicate_jobs(jobs)

    assert len(unique_jobs) == 1
    assert unique_jobs[0].job_id == "first"


def test_deduplicate_jobs_treats_trailing_slash_url_as_duplicate() -> None:
    jobs = [
        make_job(
            job_id="first",
            source_url="https://www.adzuna.com.au/jobs/details/123",
        ),
        make_job(
            job_id="second",
            source_url="https://www.adzuna.com.au/jobs/details/123/",
        ),
    ]

    unique_jobs = deduplicate_jobs(jobs)

    assert len(unique_jobs) == 1
    assert unique_jobs[0].job_id == "first"


def test_build_deduplication_key_prefers_source_url() -> None:
    job = make_job(source_url="https://www.adzuna.com.au/jobs/details/123")

    key = build_deduplication_key(job)

    assert key == "url:https://www.adzuna.com.au/jobs/details/123"


def test_normalize_key_part_normalizes_case_and_spaces() -> None:
    value = "  Junior   Backend   Developer  "

    assert normalize_key_part(value) == "junior backend developer"


def test_normalize_key_part_removes_trailing_slash() -> None:
    value = "https://www.adzuna.com.au/jobs/details/123/"

    assert normalize_key_part(value) == "https://www.adzuna.com.au/jobs/details/123"