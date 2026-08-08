from __future__ import annotations

from careervoice_ai_orchestrator.command_runner import (
    CommandResult,
    CommandRunner,
    SupportsCommandRun,
)
from careervoice_ai_orchestrator.models import WorkflowConfig


def build_job_collection_command(config: WorkflowConfig) -> list[str]:
    """
    Build the command used to call the job-listing-collector CLI.
    """
    if not config.job_queries:
        raise ValueError(
            "At least one resolved job query is required before job collection."
        )

    command = [
        "job-collect",
        "--source",
        config.job_source,
    ]

    for query in config.job_queries:
        command.extend(["--query", query])

    if config.job_location:
        command.extend(["--location", config.job_location])

    command.extend(
        [
            "--max-results",
            str(config.job_max_results),
            "--output",
            str(config.jobs_output_path),
        ]
    )

    return command


def run_job_collection(
    config: WorkflowConfig,
    runner: SupportsCommandRun | None = None,
) -> CommandResult:
    """
    Run the job collection step.

    This calls Repo 3 through its CLI and asks it to generate jobs.json.
    """
    command_runner = runner or CommandRunner()

    config.jobs_output_path.parent.mkdir(parents=True, exist_ok=True)

    return command_runner.run(build_job_collection_command(config))