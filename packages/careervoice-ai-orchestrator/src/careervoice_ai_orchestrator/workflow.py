from __future__ import annotations

from dataclasses import dataclass, replace

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
from careervoice_ai_orchestrator.query_resolution import resolve_job_queries
from careervoice_ai_orchestrator.recommendation import run_recommendations


@dataclass(frozen=True)
class WorkflowResult:
    """
    Result returned after running the full CareerVoice AI workflow.
    """

    profile_extraction_result: CommandResult | None
    job_collection_result: CommandResult
    recommendation_result: CommandResult
    job_queries: tuple[str, ...]
    profile_path: str
    jobs_output_path: str
    recommendations_output_path: str


def prepare_output_directories(config: WorkflowConfig) -> None:
    """
    Create all output directories required by the workflow.
    """
    for directory in config.output_directories:
        directory.mkdir(parents=True, exist_ok=True)


def run_workflow(
    config: WorkflowConfig,
    *,
    profile_input_text: str | None = None,
    runner: SupportsCommandRun | None = None,
) -> WorkflowResult:
    """
    Run the CareerVoice AI orchestration workflow.

    Supported input modes:

    1. profile: use an existing career_profile.json.
    2. text: save terminal text, call Repo 1, then continue.
    3. voice: call Repo 1 voice mode, then continue.

    After the profile is available, the workflow resolves one or more job
    search queries. Explicit queries take priority. When no explicit queries
    are provided, target_roles are read from the career profile.

    The workflow then runs:

    Repo 3 job collection
    → Repo 2 recommendation generation
    """
    command_runner = runner or CommandRunner()

    prepare_output_directories(config)

    profile_extraction_result: CommandResult | None = None

    if config.input_mode == "text":
        if profile_input_text is None:
            raise ValueError(
                "profile_input_text is required when input_mode is text."
            )

        save_profile_input_text(profile_input_text, config)
        profile_extraction_result = run_profile_extraction(
            config=config,
            runner=command_runner,
        )

    elif config.input_mode == "voice":
        profile_extraction_result = run_profile_extraction(
            config=config,
            runner=command_runner,
        )

    resolved_job_queries = resolve_job_queries(config)

    resolved_config = replace(
        config,
        job_queries=resolved_job_queries,
    )

    job_collection_result = run_job_collection(
        config=resolved_config,
        runner=command_runner,
    )

    recommendation_result = run_recommendations(
        config=resolved_config,
        runner=command_runner,
    )

    return WorkflowResult(
        profile_extraction_result=profile_extraction_result,
        job_collection_result=job_collection_result,
        recommendation_result=recommendation_result,
        job_queries=resolved_job_queries,
        profile_path=str(config.profile_path),
        jobs_output_path=str(config.jobs_output_path),
        recommendations_output_path=str(config.recommendations_output_path),
    )