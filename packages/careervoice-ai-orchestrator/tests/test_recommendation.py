from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from careervoice_ai_orchestrator.command_runner import CommandResult
from careervoice_ai_orchestrator.models import WorkflowConfig
from careervoice_ai_orchestrator.recommendation import (
    build_recommendation_command,
    run_recommendations,
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
            stdout="fake recommendation completed",
            stderr="",
        )


def test_build_recommendation_command_with_default_options() -> None:
    config = WorkflowConfig(
        profile_path="examples/career_profile.json",
        jobs_output_path="outputs/jobs.json",
        recommendations_output_path="outputs/recommendations.json",
        recommender_scorer="rules",
        recommendation_max_results=5,
    )

    command = build_recommendation_command(config)

    assert command == [
        "job-recommend",
        "--profile",
        "examples/career_profile.json",
        "--jobs",
        "outputs/jobs.json",
        "--max-results",
        "5",
        "--scorer",
        "rules",
        "--output",
        "outputs/recommendations.json",
    ]


def test_build_recommendation_command_with_exclude_rejected() -> None:
    config = WorkflowConfig(
        profile_path="examples/career_profile.json",
        jobs_output_path="outputs/jobs.json",
        recommendations_output_path="outputs/recommendations.json",
        recommender_scorer="rules",
        recommendation_max_results=3,
        exclude_rejected=True,
    )

    command = build_recommendation_command(config)

    assert command == [
        "job-recommend",
        "--profile",
        "examples/career_profile.json",
        "--jobs",
        "outputs/jobs.json",
        "--max-results",
        "3",
        "--exclude-rejected",
        "--scorer",
        "rules",
        "--output",
        "outputs/recommendations.json",
    ]


def test_run_recommendations_calls_runner() -> None:
    config = WorkflowConfig(
        profile_path="examples/career_profile.json",
        jobs_output_path="outputs/jobs.json",
        recommendations_output_path="outputs/recommendations.json",
        recommender_scorer="rules",
        recommendation_max_results=4,
    )
    runner = FakeRunner()

    result = run_recommendations(config, runner=runner)

    assert result.return_code == 0
    assert result.stdout == "fake recommendation completed"
    assert runner.commands == [
        (
            "job-recommend",
            "--profile",
            "examples/career_profile.json",
            "--jobs",
            "outputs/jobs.json",
            "--max-results",
            "4",
            "--scorer",
            "rules",
            "--output",
            "outputs/recommendations.json",
        )
    ]


def test_run_recommendations_creates_output_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "recommendations.json"
    config = WorkflowConfig(
        recommendations_output_path=output_path,
    )
    runner = FakeRunner()

    run_recommendations(config, runner=runner)

    assert output_path.parent.exists()