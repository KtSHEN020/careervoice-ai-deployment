from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from careervoice_ai_orchestrator.command_runner import (
    CommandResult,
    CommandRunner,
    SupportsCommandRun,
)
from careervoice_ai_orchestrator.job_collection import run_job_collection
from careervoice_ai_orchestrator.models import WorkflowConfig
from careervoice_ai_orchestrator.profile_extraction import (
    run_profile_extraction,
    save_profile_input_text,
)
from careervoice_ai_orchestrator.query_resolution import (
    load_career_profile,
    resolve_job_queries,
)
from careervoice_ai_orchestrator.recommendation import run_recommendations

__all__ = [
    "JobCollectionStageResult",
    "ProfileStageResult",
    "RecommendationStageResult",
    "collect_jobs",
    "extract_profile",
    "generate_recommendations",
    "resolve_queries",
    "save_career_profile",
]


@dataclass(frozen=True)
class ProfileStageResult:
    """
    Structured result returned after making a career profile available.
    """

    profile: dict[str, object]
    profile_path: Path
    command_result: CommandResult | None


@dataclass(frozen=True)
class JobCollectionStageResult:
    """
    Structured result returned after collecting job listings.
    """

    jobs: list[dict[str, object]]
    jobs_output_path: Path
    command_result: CommandResult


@dataclass(frozen=True)
class RecommendationStageResult:
    """
    Structured result returned after generating recommendations.
    """

    recommendations: dict[str, object]
    recommendations_output_path: Path
    command_result: CommandResult


def _load_json_file(path: Path, *, description: str) -> object:
    """
    Load one JSON file and provide a clear error when it cannot be used.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(f"{description} file was not created: {path}") from error
    except OSError as error:
        raise ValueError(f"{description} file could not be read: {path}") from error

    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"{description} file contains invalid JSON: {path}") from error


def _load_jobs(path: Path) -> list[dict[str, object]]:
    """
    Load and validate the collected jobs JSON array.
    """
    data = _load_json_file(path, description="Collected jobs")

    if not isinstance(data, list):
        raise ValueError(f"Collected jobs must contain a JSON list: {path}")

    jobs: list[dict[str, object]] = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(
                "Collected jobs must contain only JSON objects. "
                f"Invalid item at index {index}: {path}"
            )

        jobs.append(item)

    return jobs


def _load_recommendations(path: Path) -> dict[str, object]:
    """
    Load and validate the recommendation JSON object.
    """
    data = _load_json_file(path, description="Recommendations")

    if not isinstance(data, dict):
        raise ValueError(f"Recommendations must contain a JSON object: {path}")

    return data


def extract_profile(
    config: WorkflowConfig,
    *,
    profile_input_text: str | None = None,
    runner: SupportsCommandRun | None = None,
) -> ProfileStageResult:
    """
    Make a career profile available and return its structured JSON data.

    Profile mode loads an existing profile without running an external command.
    Text and voice modes call Repo 1 before loading the generated profile.
    """
    command_runner = runner or CommandRunner()
    command_result: CommandResult | None = None

    if config.input_mode == "text":
        if profile_input_text is None:
            raise ValueError(
                "profile_input_text is required when input_mode is text."
            )

        save_profile_input_text(profile_input_text, config)
        config.profile_path.unlink(missing_ok=True)
        command_result = run_profile_extraction(
            config=config,
            runner=command_runner,
        )

    elif config.input_mode == "voice":
        config.profile_path.unlink(missing_ok=True)
        command_result = run_profile_extraction(
            config=config,
            runner=command_runner,
        )

    profile = load_career_profile(config.profile_path)

    return ProfileStageResult(
        profile=profile,
        profile_path=config.profile_path,
        command_result=command_result,
    )


def save_career_profile(
    profile: Mapping[str, object],
    profile_path: str | Path,
) -> Path:
    """
    Save a reviewed or edited career profile as formatted JSON.
    """
    output_path = Path(profile_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(dict(profile), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def resolve_queries(config: WorkflowConfig) -> tuple[str, ...]:
    """
    Resolve explicit or profile-derived job queries using Repo 4 rules.
    """
    return resolve_job_queries(config)


def collect_jobs(
    config: WorkflowConfig,
    *,
    runner: SupportsCommandRun | None = None,
) -> JobCollectionStageResult:
    """
    Call Repo 3 and return the collected jobs as structured data.
    """
    config.jobs_output_path.unlink(missing_ok=True)
    command_result = run_job_collection(config=config, runner=runner)
    jobs = _load_jobs(config.jobs_output_path)

    return JobCollectionStageResult(
        jobs=jobs,
        jobs_output_path=config.jobs_output_path,
        command_result=command_result,
    )


def generate_recommendations(
    config: WorkflowConfig,
    *,
    runner: SupportsCommandRun | None = None,
) -> RecommendationStageResult:
    """
    Call Repo 2 and return the recommendation document as structured data.
    """
    config.recommendations_output_path.unlink(missing_ok=True)
    command_result = run_recommendations(config=config, runner=runner)
    recommendations = _load_recommendations(config.recommendations_output_path)

    return RecommendationStageResult(
        recommendations=recommendations,
        recommendations_output_path=config.recommendations_output_path,
        command_result=command_result,
    )