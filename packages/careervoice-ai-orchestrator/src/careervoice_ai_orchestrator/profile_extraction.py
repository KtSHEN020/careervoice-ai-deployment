from __future__ import annotations

from careervoice_ai_orchestrator.command_runner import (
    CommandResult,
    CommandRunner,
    SupportsCommandRun,
)
from careervoice_ai_orchestrator.models import WorkflowConfig


def build_text_profile_extraction_command(
    config: WorkflowConfig,
) -> list[str]:
    """
    Build the command used to call Repo 1 for text-based profile extraction.
    """
    command = [
        "career-profile-extract",
        "file",
        str(config.profile_input_path),
        "--extractor",
        config.profile_extractor,
    ]

    if config.output_language != "en":
        command.extend(
            [
                "--output-language",
                config.output_language,
            ]
        )

    command.extend(
        [
            "--output",
            str(config.profile_path),
        ]
    )

    return command


def build_voice_profile_extraction_command(
    config: WorkflowConfig,
) -> list[str]:
    """
    Build the command used to call Repo 1 for voice-based profile extraction.
    """
    command = [
        "career-profile-extract",
        "voice",
        "--extractor",
        config.profile_extractor,
    ]

    if config.output_language != "en":
        command.extend(
            [
                "--output-language",
                config.output_language,
            ]
        )

    command.extend(
        [
            "--output",
            str(config.profile_path),
        ]
    )

    return command


def build_profile_extraction_command(config: WorkflowConfig) -> list[str]:
    """
    Build the Repo 1 profile extraction command for the selected input mode.
    """
    if config.input_mode == "text":
        return build_text_profile_extraction_command(config)

    if config.input_mode == "voice":
        return build_voice_profile_extraction_command(config)

    raise ValueError(
        "Profile extraction command can only be built for text or voice mode."
    )


def save_profile_input_text(text: str, config: WorkflowConfig) -> None:
    """
    Save raw career preference text to the profile input file.
    """
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("profile input text cannot be empty.")

    config.profile_input_path.parent.mkdir(parents=True, exist_ok=True)
    config.profile_input_path.write_text(cleaned_text, encoding="utf-8")


def run_profile_extraction(
    config: WorkflowConfig,
    runner: SupportsCommandRun | None = None,
) -> CommandResult:
    """
    Run the profile extraction step.

    This calls Repo 1 through its CLI and asks it to generate career_profile.json.
    """
    command_runner = runner or CommandRunner()

    config.profile_input_path.parent.mkdir(parents=True, exist_ok=True)
    config.profile_path.parent.mkdir(parents=True, exist_ok=True)

    command = build_profile_extraction_command(config)

    if config.input_mode == "voice" and isinstance(command_runner, CommandRunner):
        return command_runner.run_interactive(command)

    return command_runner.run(command)