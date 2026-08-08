from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from careervoice_ai_orchestrator.api import (
    collect_jobs,
    extract_profile,
    generate_recommendations,
    resolve_queries,
    save_career_profile,
)
from careervoice_ai_orchestrator.command_runner import CommandResult
from careervoice_ai_orchestrator.models import WorkflowConfig


class OutputWritingFakeRunner:
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

        output_path = Path(command_tuple[command_tuple.index("--output") + 1])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if command_tuple[0] == "career-profile-extract":
            data: object = {
                "target_roles": ["software developer", "backend developer"],
                "skills": ["Python"],
            }
        elif command_tuple[0] == "job-collect":
            data = [
                {
                    "job_id": "job-1",
                    "title": "Junior Software Developer",
                }
            ]
        elif command_tuple[0] == "job-recommend":
            data = {
                "recommendations": [
                    {
                        "job_id": "job-1",
                        "match_score": 82,
                    }
                ],
                "total_jobs_scored": 1,
            }
        else:
            raise AssertionError(f"Unexpected command: {command_tuple[0]}")

        output_path.write_text(json.dumps(data), encoding="utf-8")

        return CommandResult(
            command=command_tuple,
            return_code=0,
            stdout=f"completed: {command_tuple[0]}",
            stderr="",
        )


def test_extract_profile_loads_existing_profile_without_command(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "career_profile.json"
    save_career_profile(
        {"target_roles": ["data analyst"]},
        profile_path,
    )
    runner = OutputWritingFakeRunner()
    config = WorkflowConfig(
        input_mode="profile",
        profile_path=profile_path,
    )

    result = extract_profile(config, runner=runner)

    assert result.profile == {"target_roles": ["data analyst"]}
    assert result.profile_path == profile_path
    assert result.command_result is None
    assert runner.commands == []


def test_extract_profile_runs_text_stage_and_returns_profile(
    tmp_path: Path,
) -> None:
    profile_input_path = tmp_path / "profile_input.txt"
    profile_path = tmp_path / "career_profile.json"
    runner = OutputWritingFakeRunner()
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=profile_input_path,
        profile_path=profile_path,
        profile_extractor="rules",
    )

    result = extract_profile(
        config,
        profile_input_text="I want a software developer role.",
        runner=runner,
    )

    assert profile_input_path.read_text(encoding="utf-8") == (
        "I want a software developer role."
    )
    assert result.profile["target_roles"] == [
        "software developer",
        "backend developer",
    ]
    assert result.command_result is not None
    assert runner.commands[0][0] == "career-profile-extract"


def test_extract_profile_text_mode_requires_input(tmp_path: Path) -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=tmp_path / "profile_input.txt",
        profile_path=tmp_path / "career_profile.json",
    )

    with pytest.raises(ValueError, match="profile_input_text is required"):
        extract_profile(config)


def test_save_career_profile_supports_reviewed_target_roles(
    tmp_path: Path,
) -> None:
    profile_path = tmp_path / "reviewed" / "career_profile.json"

    saved_path = save_career_profile(
        {
            "target_roles": [
                "junior backend developer",
                "Python developer",
            ],
            "skills": ["Python", "SQL"],
        },
        profile_path,
    )

    saved_data = json.loads(saved_path.read_text(encoding="utf-8"))
    assert saved_data["target_roles"] == [
        "junior backend developer",
        "Python developer",
    ]


def test_resolve_queries_uses_reviewed_profile_roles(tmp_path: Path) -> None:
    profile_path = tmp_path / "career_profile.json"
    save_career_profile(
        {
            "target_roles": [
                "junior backend developer",
                "Python developer",
            ]
        },
        profile_path,
    )
    config = WorkflowConfig(
        profile_path=profile_path,
        job_queries=(),
    )

    assert resolve_queries(config) == (
        "junior backend developer",
        "Python developer",
    )


def test_collect_jobs_returns_structured_jobs(tmp_path: Path) -> None:
    output_path = tmp_path / "jobs.json"
    runner = OutputWritingFakeRunner()
    config = WorkflowConfig(
        job_queries=("software developer", "backend developer"),
        jobs_output_path=output_path,
    )

    result = collect_jobs(config, runner=runner)

    assert result.jobs == [
        {
            "job_id": "job-1",
            "title": "Junior Software Developer",
        }
    ]
    assert result.jobs_output_path == output_path
    assert result.command_result.return_code == 0
    assert runner.commands[0][0] == "job-collect"


def test_generate_recommendations_returns_structured_document(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "recommendations.json"
    runner = OutputWritingFakeRunner()
    config = WorkflowConfig(
        recommendations_output_path=output_path,
    )

    result = generate_recommendations(config, runner=runner)

    assert result.recommendations["total_jobs_scored"] == 1
    assert result.recommendations_output_path == output_path
    assert result.command_result.return_code == 0
    assert runner.commands[0][0] == "job-recommend"