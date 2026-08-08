from __future__ import annotations

import sys

import pytest

from careervoice_ai_orchestrator.command_runner import (
    CommandNotFoundError,
    CommandRunError,
    CommandRunner,
)


def test_command_runner_returns_successful_result() -> None:
    runner = CommandRunner()

    result = runner.run(
        [
            sys.executable,
            "-c",
            "print('hello from command runner')",
        ]
    )

    assert result.return_code == 0
    assert "hello from command runner" in result.stdout
    assert result.stderr == ""


def test_command_runner_raises_when_command_fails() -> None:
    runner = CommandRunner()

    with pytest.raises(CommandRunError) as error:
        runner.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "print('command failed', file=sys.stderr); "
                    "sys.exit(3)"
                ),
            ]
        )

    assert error.value.result.return_code == 3
    assert "command failed" in error.value.result.stderr


def test_command_runner_can_return_failed_result_without_raising() -> None:
    runner = CommandRunner()

    result = runner.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.exit(5)",
        ],
        check=False,
    )

    assert result.return_code == 5


def test_command_runner_rejects_empty_command() -> None:
    runner = CommandRunner()

    with pytest.raises(ValueError, match="command cannot be empty"):
        runner.run([])


def test_command_runner_raises_when_command_is_not_found() -> None:
    runner = CommandRunner()

    with pytest.raises(CommandNotFoundError, match="Required command not found"):
        runner.run(["definitely-missing-careervoice-command"])


def test_command_runner_can_run_interactive_command() -> None:
    runner = CommandRunner()

    result = runner.run_interactive(
        [
            sys.executable,
            "-c",
            "print('interactive command completed')",
        ]
    )

    assert result.return_code == 0