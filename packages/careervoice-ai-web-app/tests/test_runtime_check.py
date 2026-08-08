from __future__ import annotations

from pathlib import Path

from careervoice_ai_web_app.runtime_check import (
    REQUIRED_RUNTIME_DEPENDENCIES,
    inspect_runtime_dependencies,
    missing_runtime_dependencies,
)


def test_inspect_runtime_dependencies_reports_available_commands() -> None:
    command_paths = {
        "career-profile-extract": "/test/bin/career-profile-extract",
        "job-collect": "/test/bin/job-collect",
        "job-recommend": "/test/bin/job-recommend",
    }

    statuses = inspect_runtime_dependencies(
        resolver=command_paths.get,
    )

    assert [status.command for status in statuses] == [
        "career-profile-extract",
        "job-collect",
        "job-recommend",
    ]
    assert all(status.available for status in statuses)
    assert statuses[0].executable_path == Path(
        "/test/bin/career-profile-extract"
    )


def test_missing_runtime_dependencies_returns_only_missing_commands() -> None:
    command_paths = {
        "career-profile-extract": "/test/bin/career-profile-extract",
        "job-collect": None,
        "job-recommend": None,
    }

    missing = missing_runtime_dependencies(
        resolver=command_paths.get,
    )

    assert [status.command for status in missing] == [
        "job-collect",
        "job-recommend",
    ]


def test_required_runtime_commands_are_installed_locally() -> None:
    statuses = inspect_runtime_dependencies()

    missing_commands = [
        status.command
        for status in statuses
        if not status.available
    ]

    assert missing_commands == [], (
        "Required CareerVoice AI commands are missing: "
        f"{', '.join(missing_commands)}"
    )


def test_all_expected_runtime_dependencies_are_declared() -> None:
    assert {
        dependency.command
        for dependency in REQUIRED_RUNTIME_DEPENDENCIES
    } == {
        "career-profile-extract",
        "job-collect",
        "job-recommend",
    }