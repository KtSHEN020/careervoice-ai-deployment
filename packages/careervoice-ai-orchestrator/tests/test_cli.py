from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from careervoice_ai_orchestrator.cli import (
    build_config_from_args,
    build_parser,
    main,
)
from careervoice_ai_orchestrator.command_runner import (
    CommandNotFoundError,
    CommandResult,
    CommandRunError,
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


class FailingRunner:
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

        raise CommandRunError(
            CommandResult(
                command=command_tuple,
                return_code=2,
                stdout="",
                stderr="fake external command failed",
            )
        )


class MissingCommandRunner:
    def run(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        raise CommandNotFoundError(command[0])


def test_build_config_from_default_cli_args() -> None:
    parser = build_parser()
    args = parser.parse_args([])

    config = build_config_from_args(args)

    assert config.profile_path == Path("examples/career_profile.json")
    assert config.jobs_output_path == Path("outputs/jobs.json")
    assert config.recommendations_output_path == Path(
        "outputs/recommendations.json"
    )
    assert config.job_source == "adzuna"
    assert config.job_queries == ()
    assert config.job_location == "Adelaide"
    assert config.job_max_results == 10
    assert config.recommender_scorer == "rules"
    assert config.recommendation_max_results == 10
    assert config.exclude_rejected is False
    assert config.input_mode == "profile"
    assert config.profile_input_path == Path("outputs/profile_input.txt")
    assert config.profile_extractor == "rules"


def test_build_config_from_custom_cli_args(tmp_path: Path) -> None:
    profile_input_path = tmp_path / "profile_input.txt"
    profile_path = tmp_path / "profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    parser = build_parser()
    args = parser.parse_args(
        [
            "--input-mode",
            "profile",
            "--profile-input",
            str(profile_input_path),
            "--profile-extractor",
            "rules",
            "--profile",
            str(profile_path),
            "--jobs-output",
            str(jobs_output_path),
            "--recommendations-output",
            str(recommendations_output_path),
            "--source",
            "adzuna",
            "--query",
            "junior python developer",
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--job-max-results",
            "5",
            "--recommendation-max-results",
            "3",
            "--scorer",
            "rules",
            "--exclude-rejected",
        ]
    )

    config = build_config_from_args(args)

    assert config.profile_path == profile_path
    assert config.jobs_output_path == jobs_output_path
    assert config.recommendations_output_path == recommendations_output_path
    assert config.job_source == "adzuna"
    assert config.job_queries == (
        "junior python developer",
        "backend developer",
    )
    assert config.job_location == "Adelaide"
    assert config.job_max_results == 5
    assert config.recommender_scorer == "rules"
    assert config.recommendation_max_results == 3
    assert config.exclude_rejected is True
    assert config.input_mode == "profile"
    assert config.profile_input_path == profile_input_path
    assert config.profile_extractor == "rules"


def test_build_config_treats_empty_location_as_none() -> None:
    parser = build_parser()
    args = parser.parse_args(["--location", ""])

    config = build_config_from_args(args)

    assert config.job_location is None


def test_build_parser_accepts_repeated_query_options() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--query",
            "software developer",
            "--query",
            "backend developer",
        ]
    )

    config = build_config_from_args(args)

    assert config.job_queries == (
        "software developer",
        "backend developer",
    )


def test_build_config_uses_output_profile_path_for_text_mode() -> None:
    parser = build_parser()
    args = parser.parse_args(["--input-mode", "text"])

    config = build_config_from_args(args)

    assert config.input_mode == "text"
    assert config.profile_path == Path("outputs/career_profile.json")


def test_main_runs_workflow_with_fake_runner(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    runner = FakeRunner()

    exit_code = main(
        [
            "--profile",
            str(profile_path),
            "--jobs-output",
            str(jobs_output_path),
            "--recommendations-output",
            str(recommendations_output_path),
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--job-max-results",
            "2",
            "--recommendation-max-results",
            "1",
            "--scorer",
            "rules",
        ],
        runner=runner,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Running CareerVoice AI orchestrator..." in captured.out
    assert "Job search queries:" in captured.out
    assert "- backend developer" in captured.out
    assert "Workflow completed successfully." in captured.out
    assert f"Jobs saved to: {jobs_output_path}" in captured.out
    assert (
        f"Recommendations saved to: {recommendations_output_path}"
        in captured.out
    )

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
            "2",
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
            "1",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]


def test_main_returns_error_when_workflow_config_is_invalid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--job-max-results",
            "0",
        ],
        runner=FakeRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "job_max_results must be at least 1" in captured.err


def test_main_returns_error_when_external_command_fails(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--query",
            "backend developer",
        ],
        runner=FailingRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Command failed with exit code 2" in captured.err
    assert "fake external command failed" in captured.err


def test_main_returns_error_when_external_command_is_missing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "--query",
            "backend developer",
        ],
        runner=MissingCommandRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Required command not found" in captured.err


def test_main_prints_external_command_output_in_verbose_mode(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    runner = FakeRunner()

    exit_code = main(
        [
            "--profile",
            str(profile_path),
            "--jobs-output",
            str(jobs_output_path),
            "--recommendations-output",
            str(recommendations_output_path),
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--job-max-results",
            "2",
            "--recommendation-max-results",
            "1",
            "--scorer",
            "rules",
            "--verbose",
        ],
        runner=runner,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Job collection output" in captured.out
    assert "completed: job-collect" in captured.out
    assert "Recommendation output" in captured.out
    assert "completed: job-recommend" in captured.out


def test_main_runs_text_input_workflow_with_fake_runner(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_input_path = tmp_path / "profile_input.txt"
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    runner = FakeRunner()

    exit_code = main(
        [
            "--input-mode",
            "text",
            "--profile-input",
            str(profile_input_path),
            "--profile",
            str(profile_path),
            "--jobs-output",
            str(jobs_output_path),
            "--recommendations-output",
            str(recommendations_output_path),
            "--profile-extractor",
            "rules",
            "--query",
            "backend developer",
            "--location",
            "Adelaide",
            "--job-max-results",
            "2",
            "--recommendation-max-results",
            "1",
            "--scorer",
            "rules",
            "--verbose",
        ],
        runner=runner,
        input_reader=lambda: (
            "I want a junior backend developer role in Adelaide."
        ),
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Workflow completed successfully." in captured.out
    assert "Job search queries:" in captured.out
    assert "- backend developer" in captured.out
    assert "Profile extraction output" in captured.out
    assert "Profile available at:" in captured.out

    assert profile_input_path.read_text(encoding="utf-8") == (
        "I want a junior backend developer role in Adelaide."
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
            "backend developer",
            "--location",
            "Adelaide",
            "--max-results",
            "2",
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
            "1",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]


def test_main_runs_voice_input_workflow_with_fake_runner(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path = tmp_path / "career_profile.json"
    jobs_output_path = tmp_path / "jobs.json"
    recommendations_output_path = tmp_path / "recommendations.json"

    runner = FakeRunner()

    exit_code = main(
        [
            "--input-mode",
            "voice",
            "--profile",
            str(profile_path),
            "--jobs-output",
            str(jobs_output_path),
            "--recommendations-output",
            str(recommendations_output_path),
            "--profile-extractor",
            "rules",
            "--query",
            "software developer",
            "--location",
            "",
            "--job-max-results",
            "2",
            "--recommendation-max-results",
            "1",
            "--scorer",
            "rules",
        ],
        runner=runner,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Starting voice input through Repo 1..." in captured.out
    assert "Job search queries:" in captured.out
    assert "- software developer" in captured.out
    assert "Workflow completed successfully." in captured.out

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
            "2",
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
            "1",
            "--scorer",
            "rules",
            "--output",
            str(recommendations_output_path),
        ),
    ]


def test_main_derives_queries_from_existing_profile(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": ["software developer", "data analyst"]}',
        encoding="utf-8",
    )
    runner = FakeRunner()

    exit_code = main(
        [
            "--input-mode",
            "profile",
            "--profile",
            str(profile_path),
        ],
        runner=runner,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Job search queries:" in captured.out
    assert "- software developer" in captured.out
    assert "- data analyst" in captured.out

    assert runner.commands[0] == (
        "job-collect",
        "--source",
        "adzuna",
        "--query",
        "software developer",
        "--query",
        "data analyst",
        "--location",
        "Adelaide",
        "--max-results",
        "10",
        "--output",
        "outputs/jobs.json",
    )


def test_main_returns_error_when_no_queries_or_target_roles(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    profile_path = tmp_path / "career_profile.json"
    profile_path.write_text(
        '{"target_roles": []}',
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--input-mode",
            "profile",
            "--profile",
            str(profile_path),
        ],
        runner=FakeRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No job search queries were provided" in captured.err
    assert "no target roles were found" in captured.err
    assert "Provide at least one --query option" in captured.err