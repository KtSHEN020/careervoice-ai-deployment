from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from careervoice_ai_orchestrator.command_runner import CommandResult
from careervoice_ai_orchestrator.models import WorkflowConfig
from careervoice_ai_orchestrator.profile_extraction import (
    build_profile_extraction_command,
    build_text_profile_extraction_command,
    build_voice_profile_extraction_command,
    run_profile_extraction,
    save_profile_input_text,
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
            stdout="fake profile extraction completed",
            stderr="",
        )


def test_build_text_profile_extraction_command() -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path="outputs/profile_input.txt",
        profile_path="outputs/career_profile.json",
        profile_extractor="rules",
    )

    command = build_text_profile_extraction_command(config)

    assert command == [
        "career-profile-extract",
        "file",
        "outputs/profile_input.txt",
        "--extractor",
        "rules",
        "--output",
        "outputs/career_profile.json",
    ]


def test_build_voice_profile_extraction_command() -> None:
    config = WorkflowConfig(
        input_mode="voice",
        profile_path="outputs/career_profile.json",
        profile_extractor="rules",
    )

    command = build_voice_profile_extraction_command(config)

    assert command == [
        "career-profile-extract",
        "voice",
        "--extractor",
        "rules",
        "--output",
        "outputs/career_profile.json",
    ]


def test_build_profile_extraction_command_for_text_mode() -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path="outputs/profile_input.txt",
        profile_path="outputs/career_profile.json",
        profile_extractor="llm",
    )

    command = build_profile_extraction_command(config)

    assert command == [
        "career-profile-extract",
        "file",
        "outputs/profile_input.txt",
        "--extractor",
        "llm",
        "--output",
        "outputs/career_profile.json",
    ]


def test_build_profile_extraction_command_for_voice_mode() -> None:
    config = WorkflowConfig(
        input_mode="voice",
        profile_path="outputs/career_profile.json",
        profile_extractor="llm",
    )

    command = build_profile_extraction_command(config)

    assert command == [
        "career-profile-extract",
        "voice",
        "--extractor",
        "llm",
        "--output",
        "outputs/career_profile.json",
    ]


def test_build_profile_extraction_command_rejects_profile_mode() -> None:
    config = WorkflowConfig(input_mode="profile")

    with pytest.raises(ValueError, match="text or voice mode"):
        build_profile_extraction_command(config)


def test_save_profile_input_text_writes_text_file(tmp_path: Path) -> None:
    input_path = tmp_path / "profile_input.txt"
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=input_path,
    )

    save_profile_input_text(
        " I want a junior Python developer role in Adelaide. ",
        config,
    )

    assert input_path.read_text(encoding="utf-8") == (
        "I want a junior Python developer role in Adelaide."
    )


def test_save_profile_input_text_rejects_empty_text(tmp_path: Path) -> None:
    input_path = tmp_path / "profile_input.txt"
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=input_path,
    )

    with pytest.raises(ValueError, match="profile input text cannot be empty"):
        save_profile_input_text("   ", config)


def test_run_profile_extraction_calls_runner_for_text_mode() -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path="outputs/profile_input.txt",
        profile_path="outputs/career_profile.json",
        profile_extractor="rules",
    )
    runner = FakeRunner()

    result = run_profile_extraction(config, runner=runner)

    assert result.return_code == 0
    assert result.stdout == "fake profile extraction completed"
    assert runner.commands == [
        (
            "career-profile-extract",
            "file",
            "outputs/profile_input.txt",
            "--extractor",
            "rules",
            "--output",
            "outputs/career_profile.json",
        )
    ]


def test_run_profile_extraction_calls_runner_for_voice_mode() -> None:
    config = WorkflowConfig(
        input_mode="voice",
        profile_path="outputs/career_profile.json",
        profile_extractor="rules",
    )
    runner = FakeRunner()

    result = run_profile_extraction(config, runner=runner)

    assert result.return_code == 0
    assert result.stdout == "fake profile extraction completed"
    assert runner.commands == [
        (
            "career-profile-extract",
            "voice",
            "--extractor",
            "rules",
            "--output",
            "outputs/career_profile.json",
        )
    ]


def test_run_profile_extraction_creates_output_directories(tmp_path: Path) -> None:
    input_path = tmp_path / "input" / "profile_input.txt"
    profile_path = tmp_path / "output" / "career_profile.json"
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path=input_path,
        profile_path=profile_path,
    )
    runner = FakeRunner()

    run_profile_extraction(config, runner=runner)

    assert input_path.parent.exists()
    assert profile_path.parent.exists()


def test_build_text_profile_extraction_command_passes_output_language() -> None:
    config = WorkflowConfig(
        input_mode="text",
        profile_input_path="outputs/profile_input.txt",
        profile_path="outputs/career_profile.json",
        profile_extractor="llm",
        output_language="zh-CN",
    )

    command = (
        build_text_profile_extraction_command(
            config
        )
    )

    assert command == [
        "career-profile-extract",
        "file",
        "outputs/profile_input.txt",
        "--extractor",
        "llm",
        "--output-language",
        "zh-CN",
        "--output",
        "outputs/career_profile.json",
    ]


def test_build_voice_profile_extraction_command_passes_output_language() -> None:
    config = WorkflowConfig(
        input_mode="voice",
        profile_path="outputs/career_profile.json",
        profile_extractor="llm",
        output_language="zh-CN",
    )

    command = (
        build_voice_profile_extraction_command(
            config
        )
    )

    assert command == [
        "career-profile-extract",
        "voice",
        "--extractor",
        "llm",
        "--output-language",
        "zh-CN",
        "--output",
        "outputs/career_profile.json",
    ]