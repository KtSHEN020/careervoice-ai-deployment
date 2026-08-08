import httpx
import pytest

from job_listing_collector.sources import AdzunaSource, SourceError, SourceRequest


def make_adzuna_result() -> dict:
    return {
        "id": "123",
        "title": "Junior Python Developer",
        "company": {
            "display_name": "Example Tech",
        },
        "location": {
            "display_name": "Adelaide SA",
            "area": ["Australia", "South Australia", "Adelaide"],
        },
        "description": "Build and maintain Python services.",
        "redirect_url": "https://www.adzuna.com.au/jobs/details/123",
        "category": {
            "label": "IT Jobs",
        },
    }


def make_mock_client(
    status_code: int = 200,
    json_data: dict | None = None,
    content: bytes | None = None,
    captured_requests: list[httpx.Request] | None = None,
) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if captured_requests is not None:
            captured_requests.append(request)

        if content is not None:
            return httpx.Response(status_code, content=content)

        return httpx.Response(status_code, json=json_data or {})

    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_adzuna_source_collects_raw_jobs() -> None:
    client = make_mock_client(json_data={"results": [make_adzuna_result()]})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )
    request = SourceRequest(
        query="junior developer",
        location="Adelaide",
        max_results=5,
    )

    jobs = source.collect(request)

    assert len(jobs) == 1
    assert jobs[0].source == "adzuna"
    assert jobs[0].source_job_id == "123"
    assert jobs[0].title == "Junior Python Developer"
    assert jobs[0].company == "Example Tech"
    assert jobs[0].location == "Adelaide SA"
    assert jobs[0].description == "Build and maintain Python services."
    assert jobs[0].source_url == "https://www.adzuna.com.au/jobs/details/123"


def test_adzuna_source_sends_expected_query_parameters() -> None:
    captured_requests: list[httpx.Request] = []
    client = make_mock_client(
        json_data={"results": [make_adzuna_result()]},
        captured_requests=captured_requests,
    )
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )
    request = SourceRequest(
        query="junior developer",
        location="Adelaide",
        max_results=5,
    )

    source.collect(request)

    assert len(captured_requests) == 1

    sent_request = captured_requests[0]
    params = dict(sent_request.url.params)

    assert str(sent_request.url).startswith(
        "https://api.adzuna.com/v1/api/jobs/au/search/1"
    )
    assert params["app_id"] == "test-app-id"
    assert params["app_key"] == "test-app-key"
    assert params["what"] == "junior developer"
    assert params["where"] == "Adelaide"
    assert params["results_per_page"] == "5"
    assert params["content-type"] == "application/json"


def test_adzuna_source_omits_location_when_not_provided() -> None:
    captured_requests: list[httpx.Request] = []
    client = make_mock_client(
        json_data={"results": [make_adzuna_result()]},
        captured_requests=captured_requests,
    )
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )
    request = SourceRequest(
        query="junior developer",
        location=None,
        max_results=5,
    )

    source.collect(request)

    params = dict(captured_requests[0].url.params)

    assert "where" not in params


def test_adzuna_source_uses_custom_country() -> None:
    captured_requests: list[httpx.Request] = []
    client = make_mock_client(
        json_data={"results": [make_adzuna_result()]},
        captured_requests=captured_requests,
    )
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        country="gb",
        client=client,
    )

    source.collect(SourceRequest(query="junior developer"))

    assert str(captured_requests[0].url).startswith(
        "https://api.adzuna.com/v1/api/jobs/gb/search/1"
    )


def test_adzuna_source_uses_location_area_when_display_name_missing() -> None:
    result = make_adzuna_result()
    result["location"] = {
        "area": ["Australia", "South Australia", "Adelaide"],
    }
    client = make_mock_client(json_data={"results": [result]})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    jobs = source.collect(SourceRequest(query="junior developer"))

    assert jobs[0].location == "Australia, South Australia, Adelaide"


def test_adzuna_source_uses_defaults_for_missing_optional_fields() -> None:
    result = {
        "id": "123",
        "redirect_url": "https://www.adzuna.com.au/jobs/details/123",
    }
    client = make_mock_client(json_data={"results": [result]})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    jobs = source.collect(SourceRequest(query="junior developer"))

    assert jobs[0].title == "Untitled job"
    assert jobs[0].company == "Unknown company"
    assert jobs[0].location == "Unknown location"
    assert jobs[0].description == "Untitled job"


def test_adzuna_source_skips_records_without_traceable_url() -> None:
    result = make_adzuna_result()
    del result["redirect_url"]

    client = make_mock_client(json_data={"results": [result]})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    jobs = source.collect(SourceRequest(query="junior developer"))

    assert jobs == []


def test_adzuna_source_raises_source_error_for_http_error() -> None:
    client = make_mock_client(status_code=500, json_data={"error": "server error"})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    with pytest.raises(SourceError, match="status 500"):
        source.collect(SourceRequest(query="junior developer"))


def test_adzuna_source_raises_source_error_for_invalid_json() -> None:
    client = make_mock_client(status_code=200, content=b"not valid json")
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    with pytest.raises(SourceError, match="not valid JSON"):
        source.collect(SourceRequest(query="junior developer"))


def test_adzuna_source_raises_source_error_for_missing_results_list() -> None:
    client = make_mock_client(json_data={"unexpected": []})
    source = AdzunaSource(
        app_id="test-app-id",
        app_key="test-app-key",
        client=client,
    )

    with pytest.raises(SourceError, match="valid results list"):
        source.collect(SourceRequest(query="junior developer"))


def test_adzuna_source_rejects_empty_credentials() -> None:
    with pytest.raises(ValueError, match="app_id"):
        AdzunaSource(app_id=" ", app_key="test-app-key")

    with pytest.raises(ValueError, match="app_key"):
        AdzunaSource(app_id="test-app-id", app_key=" ")