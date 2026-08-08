import pytest
from pydantic import ValidationError

from job_listing_collector.sources import JobSource, RawJobRecord, SourceRequest


def make_valid_raw_job_data() -> dict:
    return {
        "source": "adzuna",
        "source_job_id": "123",
        "title": "Junior Developer",
        "company": "Example Tech",
        "location": "Adelaide",
        "description": "Build software features.",
        "source_url": "https://example.com/jobs/123",
        "raw_data": {"category": "IT Jobs"},
    }


def test_source_request_can_be_created() -> None:
    request = SourceRequest(
        query="junior developer",
        location="Adelaide",
        max_results=5,
    )

    assert request.query == "junior developer"
    assert request.location == "Adelaide"
    assert request.max_results == 5


def test_source_request_strips_query_and_location() -> None:
    request = SourceRequest(
        query="  junior developer  ",
        location="  Adelaide  ",
    )

    assert request.query == "junior developer"
    assert request.location == "Adelaide"


def test_source_request_converts_empty_location_to_none() -> None:
    request = SourceRequest(
        query="junior developer",
        location="   ",
    )

    assert request.location is None


def test_source_request_rejects_empty_query() -> None:
    with pytest.raises(ValidationError):
        SourceRequest(query="   ")


def test_source_request_rejects_invalid_max_results() -> None:
    with pytest.raises(ValidationError):
        SourceRequest(query="junior developer", max_results=0)

    with pytest.raises(ValidationError):
        SourceRequest(query="junior developer", max_results=101)


def test_raw_job_record_can_be_created() -> None:
    raw_job = RawJobRecord(**make_valid_raw_job_data())

    assert raw_job.source == "adzuna"
    assert raw_job.source_job_id == "123"
    assert raw_job.title == "Junior Developer"
    assert raw_job.company == "Example Tech"
    assert raw_job.location == "Adelaide"
    assert raw_job.raw_data == {"category": "IT Jobs"}


def test_raw_job_record_strips_required_strings() -> None:
    data = make_valid_raw_job_data()
    data["title"] = "  Junior Developer  "

    raw_job = RawJobRecord(**data)

    assert raw_job.title == "Junior Developer"


def test_raw_job_record_rejects_empty_required_string() -> None:
    data = make_valid_raw_job_data()
    data["title"] = "   "

    with pytest.raises(ValidationError):
        RawJobRecord(**data)


def test_raw_job_record_rejects_extra_field() -> None:
    data = make_valid_raw_job_data()
    data["salary"] = "$70,000"

    with pytest.raises(ValidationError):
        RawJobRecord(**data)


def test_job_source_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        JobSource()


def test_dummy_source_can_implement_interface() -> None:
    class DummySource(JobSource):
        source_name = "dummy"

        def collect(self, request: SourceRequest) -> list[RawJobRecord]:
            return [
                RawJobRecord(
                    source=self.source_name,
                    source_job_id="dummy-001",
                    title=f"{request.query.title()} Role",
                    company="Example Tech",
                    location=request.location or "Remote",
                    description="Example job description.",
                    source_url="https://example.com/jobs/dummy-001",
                    raw_data={"max_results": request.max_results},
                )
            ]

    source = DummySource()
    request = SourceRequest(query="python developer", location="Adelaide")
    jobs = source.collect(request)

    assert len(jobs) == 1
    assert jobs[0].source == "dummy"
    assert jobs[0].title == "Python Developer Role"
    assert jobs[0].location == "Adelaide"