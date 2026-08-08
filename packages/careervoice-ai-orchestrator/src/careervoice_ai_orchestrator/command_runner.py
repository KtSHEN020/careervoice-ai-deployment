from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """
    Result returned after running an external command.
    """

    command: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str


class SupportsCommandRun(Protocol):
    """
    Protocol for objects that can run external commands.

    Production code can use CommandRunner.
    Tests can use fake runners.
    """

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        """
        Run an external command.
        """


class CommandRunError(RuntimeError):
    """
    Raised when an external command exits with a non-zero status code.
    """

    def __init__(self, result: CommandResult) -> None:
        self.result = result

        command_text = " ".join(result.command)
        message = f"Command failed with exit code {result.return_code}: {command_text}"

        if result.stderr.strip():
            message = f"{message}\nSTDERR:\n{result.stderr.strip()}"

        super().__init__(message)


class CommandNotFoundError(RuntimeError):
    """
    Raised when the requested external CLI command cannot be found.
    """

    def __init__(self, command_name: str) -> None:
        self.command_name = command_name

        message = (
            f"Required command not found: {command_name}. "
            "Make sure the related repository is installed in this environment."
        )

        super().__init__(message)


class CommandRunner:
    """
    Runs external CLI commands for the orchestrator.

    The orchestrator will use this class to call tools from the other
    CareerVoice AI repositories, such as job-collect and job-recommend.
    """

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        """
        Run a command and return a structured result.
        """
        if not command:
            raise ValueError("command cannot be empty.")

        command_tuple = tuple(str(part) for part in command)

        process_env = os.environ.copy()
        if env is not None:
            process_env.update(env)

        try:
            completed_process = subprocess.run(
                list(command_tuple),
                cwd=Path(cwd) if cwd is not None else None,
                env=process_env,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except FileNotFoundError as error:
            raise CommandNotFoundError(command_tuple[0]) from error

        result = CommandResult(
            command=command_tuple,
            return_code=completed_process.returncode,
            stdout=completed_process.stdout,
            stderr=completed_process.stderr,
        )

        if check and result.return_code != 0:
            raise CommandRunError(result)

        return result

    def run_interactive(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        """
        Run an interactive command using the terminal directly.

        This is useful for commands that need microphone access, terminal prompts,
        or direct user interaction.
        """
        if not command:
            raise ValueError("command cannot be empty.")

        command_tuple = tuple(str(part) for part in command)

        process_env = os.environ.copy()
        if env is not None:
            process_env.update(env)

        try:
            completed_process = subprocess.run(
                list(command_tuple),
                cwd=Path(cwd) if cwd is not None else None,
                env=process_env,
                check=False,
                timeout=timeout_seconds,
            )
        except FileNotFoundError as error:
            raise CommandNotFoundError(command_tuple[0]) from error

        result = CommandResult(
            command=command_tuple,
            return_code=completed_process.returncode,
            stdout="",
            stderr="",
        )

        if check and result.return_code != 0:
            raise CommandRunError(result)

        return result