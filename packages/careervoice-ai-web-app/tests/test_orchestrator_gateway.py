from __future__ import annotations

from pathlib import Path

import pytest
from careervoice_ai_orchestrator import api as orchestrator_api
from careervoice_ai_orchestrator.api import (
    JobCollectionStageResult,
    ProfileStageResult,
)
from careervoice_ai_orchestrator.command_runner import (
    CommandNotFoundError,
    CommandResult,
    CommandRunError,
)
from careervoice_ai_orchestrator.models import WorkflowConfig

from careervoice_ai_web_app.errors import OrchestrationError
from careervoice_ai_web_app.orchestrator_gateway import Repo4OrchestratorGateway


def test_extract_profile_returns_structured_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=tmp_path / "profile_input.txt",
        profile_path=tmp_path / "career_profile.json",
    )
    expected_profile = {
        "target_roles": ["software developer"],
        "skills": ["Python"],
    }

    def fake_extract_profile(
        received_config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> ProfileStageResult:
        assert received_config == config
        assert profile_input_text == "I want a software developer role."
        return ProfileStageResult(
            profile=expected_profile,
            profile_path=config.profile_path,
            command_result=None,
        )

    monkeypatch.setattr(
        orchestrator_api,
        "extract_profile",
        fake_extract_profile,
    )

    gateway = Repo4OrchestratorGateway()
    profile = gateway.extract_profile(
        config,
        profile_input_text="I want a software developer role.",
    )

    assert profile == expected_profile


def test_resolve_queries_returns_repo4_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = WorkflowConfig(job_queries=("backend developer",))

    monkeypatch.setattr(
        orchestrator_api,
        "resolve_queries",
        lambda received_config: received_config.job_queries,
    )

    gateway = Repo4OrchestratorGateway()

    assert gateway.resolve_queries(config) == ("backend developer",)


def test_collect_jobs_returns_structured_jobs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = WorkflowConfig(
        job_queries=("software developer",),
        jobs_output_path=tmp_path / "jobs.json",
    )
    expected_jobs = [
        {
            "job_id": "job-1",
            "title": "Junior Software Developer",
        }
    ]
    command_result = CommandResult(
        command=("job-collect",),
        return_code=0,
        stdout="completed",
        stderr="",
    )

    monkeypatch.setattr(
        orchestrator_api,
        "collect_jobs",
        lambda received_config: JobCollectionStageResult(
            jobs=expected_jobs,
            jobs_output_path=received_config.jobs_output_path,
            command_result=command_result,
        ),
    )

    gateway = Repo4OrchestratorGateway()

    assert gateway.collect_jobs(config) == expected_jobs


def test_missing_cli_is_converted_to_web_safe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = WorkflowConfig(input_mode="text")

    def raise_missing_command(
        received_config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> ProfileStageResult:
        del received_config, profile_input_text
        raise CommandNotFoundError("career-profile-extract")

    monkeypatch.setattr(
        orchestrator_api,
        "extract_profile",
        raise_missing_command,
    )

    gateway = Repo4OrchestratorGateway()

    with pytest.raises(OrchestrationError) as error_info:
        gateway.extract_profile(config, profile_input_text="test input")

    error = error_info.value
    assert error.stage == "profile extraction"
    assert "required CareerVoice AI component" in error.user_message
    assert error.technical_details is not None
    assert "career-profile-extract" in error.technical_details


def test_command_failure_preserves_technical_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = WorkflowConfig(job_queries=("data analyst",))
    command_result = CommandResult(
        command=("job-collect",),
        return_code=1,
        stdout="",
        stderr="Adzuna request failed",
    )

    def raise_command_failure(
        received_config: WorkflowConfig,
    ) -> JobCollectionStageResult:
        del received_config
        raise CommandRunError(command_result)

    monkeypatch.setattr(
        orchestrator_api,
        "collect_jobs",
        raise_command_failure,
    )

    gateway = Repo4OrchestratorGateway()

    with pytest.raises(OrchestrationError) as error_info:
        gateway.collect_jobs(config)

    error = error_info.value
    assert error.stage == "job collection"
    assert error.user_message == "Job collection could not be completed."
    assert error.technical_details is not None
    assert "Adzuna request failed" in error.technical_details


def test_value_error_keeps_clear_repo4_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = WorkflowConfig()
    message = "No explicit job queries or profile target roles were provided."

    def raise_value_error(received_config: WorkflowConfig) -> tuple[str, ...]:
        del received_config
        raise ValueError(message)

    monkeypatch.setattr(
        orchestrator_api,
        "resolve_queries",
        raise_value_error,
    )

    gateway = Repo4OrchestratorGateway()

    with pytest.raises(OrchestrationError) as error_info:
        gateway.resolve_queries(config)

    assert error_info.value.user_message == message