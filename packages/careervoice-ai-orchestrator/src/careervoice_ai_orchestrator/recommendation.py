from __future__ import annotations

from careervoice_ai_orchestrator.command_runner import (
    CommandResult,
    CommandRunner,
    SupportsCommandRun,
)
from careervoice_ai_orchestrator.models import WorkflowConfig


def build_recommendation_command(config: WorkflowConfig) -> list[str]:
    """
    Build the command used to call the preference-aware-job-recommender CLI.
    """
    command = [
        "job-recommend",
        "--profile",
        str(config.profile_path),
        "--jobs",
        str(config.jobs_output_path),
        "--max-results",
        str(config.recommendation_max_results),
    ]

    if config.exclude_rejected:
        command.append("--exclude-rejected")

    command.extend(
        [
            "--scorer",
            config.recommender_scorer,
            "--output",
            str(config.recommendations_output_path),
        ]
    )

    return command


def run_recommendations(
    config: WorkflowConfig,
    runner: SupportsCommandRun | None = None,
) -> CommandResult:
    """
    Run the recommendation step.

    This calls Repo 2 through its CLI and asks it to generate recommendations.json.
    """
    command_runner = runner or CommandRunner()

    config.recommendations_output_path.parent.mkdir(parents=True, exist_ok=True)

    return command_runner.run(build_recommendation_command(config))