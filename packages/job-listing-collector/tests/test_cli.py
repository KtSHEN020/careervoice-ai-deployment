import json
from pathlib import Path

import pytest

from job_listing_collector import cli
from job_listing_collector.sources import RawJobRecord, SourceError, SourceRequest


class FakeSource:
    source_name = "fake"

    def __init__(self, raw_jobs: list[RawJobRecord] | None = None) -> None:
        self.raw_jobs = raw_jobs or []
        self.received_request: SourceRequest | None = None
        self.received_requests: list[SourceRequest] = []

    def collect(self, request: SourceRequest) -> list[RawJobRecord]:
        self.received_request = request
        self.received_requests.append(request)
        return self.raw_jobs


def make_raw_job(
    *,
    source_job_id: str = "123",
    source_url: str = "https://www.adzuna.com.au/jobs/details/123",
) -> RawJobRecord:
    return RawJobRecord(
        source="adzuna",
        source_job_id=source_job_id,
        title="Junior Backend Developer",
        company="Example Tech",
        location="Adelaide SA",
        description=(
            "Build backend APIs using Python, SQL, and Git. "
            "Docker is preferred."
        ),
        source_url=source_url,
        raw_data={"category": "IT Jobs"},
    )


def test_build_parser_parses_expected_arguments() -> None:
    parser = cli.build_parser()

    args = parser.parse_args(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--location",
            "Adelaide",
            "--max-results",
            "5",
            "--output",
            "outputs/jobs.json",
        ]
    )

    assert args.source == "adzuna"
    assert args.queries == ["junior developer"]
    assert args.location == "Adelaide"
    assert args.max_results == 5
    assert args.output == "outputs/jobs.json"
    assert args.normalizer == "rule"


def test_build_parser_accepts_multiple_queries() -> None:
    parser = cli.build_parser()

    args = parser.parse_args(
        [
            "--source",
            "adzuna",
            "--query",
            "software developer",
            "--query",
            "backend developer",
            "--query",
            "data analyst",
        ]
    )

    assert args.queries == [
        "software developer",
        "backend developer",
        "data analyst",
    ]


def test_build_parser_accepts_underscore_max_results_alias() -> None:
    parser = cli.build_parser()

    args = parser.parse_args(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--max_results",
            "5",
        ]
    )

    assert args.max_results == 5


def test_normalize_queries_cleans_and_deduplicates_values() -> None:
    queries = cli.normalize_queries(
        [
            " software developer ",
            "backend developer",
            "Software Developer",
            "data analyst",
            "BACKEND DEVELOPER",
        ]
    )

    assert queries == [
        "software developer",
        "backend developer",
        "data analyst",
    ]


def test_normalize_queries_rejects_empty_values() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        cli.normalize_queries(["software developer", "   "])


def test_main_collects_normalizes_deduplicates_and_exports(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "jobs.json"
    fake_source = FakeSource(
        raw_jobs=[
            make_raw_job(),
            make_raw_job(source_job_id="duplicate"),
        ]
    )

    monkeypatch.setattr(cli, "create_adzuna_source", lambda: fake_source)

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--location",
            "Adelaide",
            "--max-results",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    exported_data = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert output_path.exists()
    assert len(exported_data) == 1
    assert exported_data[0]["job_id"] == "adzuna_123"
    assert exported_data[0]["title"] == "Junior Backend Developer"
    assert exported_data[0]["required_skills"] == ["Python", "SQL", "Git"]
    assert exported_data[0]["preferred_skills"] == ["Docker"]
    assert 'Query "junior developer": collected 2 raw jobs.' in captured.out
    assert "Collected 2 raw jobs from adzuna across 1 query." in captured.out
    assert "Normalized 2 jobs." in captured.out
    assert "Exported 1 unique jobs" in captured.out


def test_main_passes_request_values_to_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "jobs.json"
    fake_source = FakeSource(raw_jobs=[])

    monkeypatch.setattr(cli, "create_adzuna_source", lambda: fake_source)

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "python developer",
            "--location",
            "Adelaide",
            "--max-results",
            "7",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert fake_source.received_request is not None
    assert fake_source.received_request.query == "python developer"
    assert fake_source.received_request.location == "Adelaide"
    assert fake_source.received_request.max_results == 7


def test_main_collects_multiple_queries_and_deduplicates_combined_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "jobs.json"
    fake_source = FakeSource(raw_jobs=[make_raw_job()])

    monkeypatch.setattr(cli, "create_adzuna_source", lambda: fake_source)

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "software developer",
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--max-results",
            "5",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    exported_data = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0

    assert [request.query for request in fake_source.received_requests] == [
        "software developer",
        "backend developer",
    ]

    assert all(
        request.location == "Adelaide"
        for request in fake_source.received_requests
    )

    assert all(
        request.max_results == 5
        for request in fake_source.received_requests
    )

    # FakeSource returns the same job for both queries, so the combined output
    # should contain one job after cross-query deduplication.
    assert len(exported_data) == 1
    assert exported_data[0]["job_id"] == "adzuna_123"

    assert 'Query "software developer": collected 1 raw jobs.' in captured.out
    assert 'Query "backend developer": collected 1 raw jobs.' in captured.out
    assert "Collected 2 raw jobs from adzuna across 2 queries." in captured.out
    assert "Exported 1 unique jobs" in captured.out


def test_main_returns_error_when_source_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "jobs.json"

    class FailingSource:
        def collect(self, request: SourceRequest) -> list[RawJobRecord]:
            raise SourceError("source failed")

    monkeypatch.setattr(cli, "create_adzuna_source", lambda: FailingSource())

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error: source failed" in captured.err
    assert not output_path.exists()


def test_main_returns_error_when_config_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "jobs.json"

    def raise_config_error() -> None:
        raise RuntimeError("ADZUNA_APP_ID is not set")

    monkeypatch.setattr(cli, "create_adzuna_source", raise_config_error)

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error: ADZUNA_APP_ID is not set" in captured.err
    assert not output_path.exists()


def test_main_returns_error_for_invalid_max_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "jobs.json"

    exit_code = cli.main(
        [
            "--source",
            "adzuna",
            "--query",
            "junior developer",
            "--max-results",
            "0",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "max_results" in captured.err
    assert not output_path.exists()


def test_create_source_rejects_unsupported_source() -> None:
    with pytest.raises(ValueError, match="Unsupported source"):
        cli.create_source("unknown")