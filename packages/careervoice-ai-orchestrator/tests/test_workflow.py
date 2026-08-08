from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from careervoice_ai_orchestrator.command_runner import CommandResult
from careervoice_ai_orchestrator.models import WorkflowConfig
from careervoice_ai_orchestrator.workflow import (
    prepare_output_directories,
    run_workflow,
)


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
            stdout=f"completed: {command_tuple[0]}",
            stderr="",
        )


def test_prepare_output_directories_creates_required_directories(
    tmp_path: Path,
) -> None:
    jobs_output_path = tmp_path / "job_outputs" / "jobs.json"
    recommendations_output_path = (
        tmp_path / "recommendation_outputs" / "recommendations.json"
    )

    config = WorkflowConfig(
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
    )

    prepare_output_directories(config)

    assert jobs_output_path.parent.exists()
    assert recommendations_output_path.parent.exists()


def test_run_workflow_runs_job_collection_then_recommendations(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    config = WorkflowConfig(
        profile_path=profile_path,
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
        job_queries=("junior python developer",),
        job_location="Adelaide",
        job_max_results=5,
        recommender_scorer="rules",
        recommendation_max_results=3,
    )
    runner = FakeRunner()

    result = run_workflow(config=config, runner=runner)

    assert runner.commands == [
        (
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
            str(jobs_output_path),
        ),
        (
            "job-recommend",
            "--profile",
            str(profile_path),
            "--jobs",
            str(jobs_output_path),
            "--max-results",
            "3",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]

    assert result.job_collection_result.return_code == 0
    assert result.recommendation_result.return_code == 0
    assert result.jobs_output_path == str(jobs_output_path)
    assert result.recommendations_output_path == str(
        recommendations_output_path
    )


def test_run_workflow_creates_output_directories(tmp_path: Path) -> None:
    jobs_output_path = tmp_path / "outputs" / "jobs" / "jobs.json"
    recommendations_output_path = (
        tmp_path / "outputs" / "recommendations" / "recommendations.json"
    )

    config = WorkflowConfig(
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
        job_queries=("software developer",),
    )
    runner = FakeRunner()

    run_workflow(config=config, runner=runner)

    assert jobs_output_path.parent.exists()
    assert recommendations_output_path.parent.exists()


def test_run_workflow_with_text_input_runs_profile_extraction_first(
    tmp_path: Path,
) -> None:
    profile_input_path = tmp_path / "profile_input.txt"
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=profile_input_path,
        profile_path=profile_path,
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
        profile_extractor="rules",
        job_queries=("junior python developer",),
        job_location="Adelaide",
        job_max_results=5,
        recommender_scorer="rules",
        recommendation_max_results=3,
    )
    runner = FakeRunner()

    result = run_workflow(
        config=config,
        profile_input_text=(
            "I want a junior Python developer role in Adelaide."
        ),
        runner=runner,
    )

    assert profile_input_path.read_text(encoding="utf-8") == (
        "I want a junior Python developer role in Adelaide."
    )

    assert runner.commands == [
        (
            "career-profile-extract",
            "file",
            str(profile_input_path),
            "--extractor",
            "rules",
            "--output",
            str(profile_path),
        ),
        (
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
            str(jobs_output_path),
        ),
        (
            "job-recommend",
            "--profile",
            str(profile_path),
            "--jobs",
            str(jobs_output_path),
            "--max-results",
            "3",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]

    assert result.profile_extraction_result is not None
    assert result.profile_path == str(profile_path)


def test_run_workflow_with_text_input_requires_text(tmp_path: Path) -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=tmp_path / "profile_input.txt",
        profile_path=tmp_path / "career_profile.json",
    )
    runner = FakeRunner()

    try:
        run_workflow(config=config, runner=runner)
    except ValueError as error:
        assert "profile_input_text is required" in str(error)
    else:
        raise AssertionError("Expected ValueError to be raised.")


def test_run_workflow_with_voice_input_runs_profile_extraction_first(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    config = WorkflowConfig(
        input_mode="voice",
        profile_path=profile_path,
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
        profile_extractor="rules",
        job_queries=("software developer",),
        job_location=None,
        job_max_results=4,
        recommender_scorer="rules",
        recommendation_max_results=2,
    )
    runner = FakeRunner()

    result = run_workflow(config=config, runner=runner)

    assert runner.commands == [
        (
            "career-profile-extract",
            "voice",
            "--extractor",
            "rules",
            "--output",
            str(profile_path),
        ),
        (
            "job-collect",
            "--source",
            "adzuna",
            "--query",
            "software developer",
            "--max-results",
            "4",
            "--output",
            str(jobs_output_path),
        ),
        (
            "job-recommend",
            "--profile",
            str(profile_path),
            "--jobs",
            str(jobs_output_path),
            "--max-results",
            "2",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]

    assert result.profile_extraction_result is not None


def test_run_workflow_derives_multiple_queries_from_profile(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": ["software developer", "backend developer"]}',
        encoding="utf-8",
    )
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    config = WorkflowConfig(
        input_mode="profile",
        profile_path=profile_path,
        jobs_output_path=jobs_output_path,
        recommendations_output_path=recommendations_output_path,
        job_location="Adelaide",
        job_max_results=5,
        recommendation_max_results=3,
    )
    runner = FakeRunner()

    result = run_workflow(config=config, runner=runner)

    assert result.job_queries == (
        "software developer",
        "backend developer",
    )
    assert runner.commands[0] == (
        "job-collect",
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
        str(jobs_output_path),
    )


def test_run_workflow_uses_explicit_queries_instead_of_profile(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": ["data analyst"]}',
        encoding="utf-8",
    )
    config = WorkflowConfig(
        profile_path=profile_path,
        job_queries=(
            "software developer",
            "backend developer",
        ),
    )
    runner = FakeRunner()

    result = run_workflow(config=config, runner=runner)

    assert result.job_queries == (
        "software developer",
        "backend developer",
    )
    assert runner.commands[0][3:] == (
        "--query",
        "software developer",
        "--query",
        "backend developer",
        "--location",
        "Adelaide",
        "--max-results",
        "10",
        "--output",
        "outputs/jobs.json",
    )