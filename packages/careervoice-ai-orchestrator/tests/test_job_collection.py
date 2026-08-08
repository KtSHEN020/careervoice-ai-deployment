from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from careervoice_ai_orchestrator.command_runner import CommandResult
from careervoice_ai_orchestrator.job_collection import (
    build_job_collection_command,
    run_job_collection,
)
from careervoice_ai_orchestrator.models import WorkflowConfig


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[tuple[str, ...]] = []

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        command_tuple = tuple(command)
        self.commands.append(command_tuple)

        return CommandResult(
            command=command_tuple,
            return_code=0,
            stdout="fake job collection completed",
            stderr="",
        )


def test_build_job_collection_command_with_location() -> None:
    config = WorkflowConfig(
        job_source="adzuna",
        job_queries=("junior python developer",),
        job_location="Adelaide",
        job_max_results=5,
        jobs_output_path="outputs/jobs.json",
    )

    command = build_job_collection_command(config)

    assert command == [
        "job-collect",
        "--source",
        "adzuna",
        "--query",
        "junior python developer",
        "--location",
        "Adelaide",
        "--max-results",
        "5",
        "--output",
        "outputs/jobs.json",
    ]


def test_build_job_collection_command_without_location() -> None:
    config = WorkflowConfig(
        job_queries=("data analyst",),
        job_location=None,
        jobs_output_path="outputs/jobs.json",
    )

    command = build_job_collection_command(config)

    assert command == [
        "job-collect",
        "--source",
        "adzuna",
        "--query",
        "data analyst",
        "--max-results",
        "10",
        "--output",
        "outputs/jobs.json",
    ]


def test_run_job_collection_calls_runner() -> None:
    config = WorkflowConfig(
        job_queries=("backend developer",),
        job_location="Adelaide",
        job_max_results=3,
        jobs_output_path="outputs/jobs.json",
    )
    runner = FakeRunner()

    result = run_job_collection(config, runner=runner)

    assert result.return_code == 0
    assert result.stdout == "fake job collection completed"
    assert runner.commands == [
        (
            "job-collect",
            "--source",
            "adzuna",
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--max-results",
            "3",
            "--output",
            "outputs/jobs.json",
        )
    ]


def test_run_job_collection_creates_output_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "jobs.json"
    config = WorkflowConfig(
        job_queries=("software developer",),
        jobs_output_path=output_path,
    )
    runner = FakeRunner()

    run_job_collection(config, runner=runner)

    assert output_path.parent.exists()


def test_build_job_collection_command_with_multiple_queries() -> None:
    config = WorkflowConfig(
        job_source="adzuna",
        job_queries=(
            "software developer",
            "backend developer",
            "data analyst",
        ),
        job_location="Adelaide",
        job_max_results=5,
        jobs_output_path="outputs/jobs.json",
    )

    command = build_job_collection_command(config)

    assert command == [
        "job-collect",
        "--source",
        "adzuna",
        "--query",
        "software developer",
        "--query",
        "backend developer",
        "--query",
        "data analyst",
        "--location",
        "Adelaide",
        "--max-results",
        "5",
        "--output",
        "outputs/jobs.json",
    ]


def test_build_job_collection_command_requires_resolved_queries() -> None:
    config = WorkflowConfig(job_queries=())

    try:
        build_job_collection_command(config)
    except ValueError as error:
        assert "At least one resolved job query" in str(error)
    else:
        raise AssertionError("Expected ValueError to be raised.")