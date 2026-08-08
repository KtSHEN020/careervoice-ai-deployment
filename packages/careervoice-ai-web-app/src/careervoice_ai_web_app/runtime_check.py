from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

CommandResolver = Callable[[str], str | None]


@dataclass(frozen=True)
class RuntimeDependency:
    """One command required by the integrated CareerVoice AI workflow."""

    command: str
    purpose: str


@dataclass(frozen=True)
class RuntimeDependencyStatus:
    """Availability information for one required runtime command."""

    command: str
    purpose: str
    executable_path: Path | None

    @property
    def available(self) -> bool:
        """Return whether the command is available in the current environment."""
        return self.executable_path is not None


REQUIRED_RUNTIME_DEPENDENCIES = (
    RuntimeDependency(
        command="career-profile-extract",
        purpose="career profile extraction",
    ),
    RuntimeDependency(
        command="job-collect",
        purpose="job listing collection",
    ),
    RuntimeDependency(
        command="job-recommend",
        purpose="job recommendation generation",
    ),
)


def inspect_runtime_dependencies(
    *,
    resolver: CommandResolver = shutil.which,
) -> tuple[RuntimeDependencyStatus, ...]:
    """Inspect all external CLI commands required by Repo 4."""
    statuses: list[RuntimeDependencyStatus] = []

    for dependency in REQUIRED_RUNTIME_DEPENDENCIES:
        resolved_path = resolver(dependency.command)

        statuses.append(
            RuntimeDependencyStatus(
                command=dependency.command,
                purpose=dependency.purpose,
                executable_path=(
                    Path(resolved_path) if resolved_path is not None else None
                ),
            )
        )

    return tuple(statuses)


def missing_runtime_dependencies(
    *,
    resolver: CommandResolver = shutil.which,
) -> tuple[RuntimeDependencyStatus, ...]:
    """Return required CLI commands that are unavailable."""
    return tuple(
        status
        for status in inspect_runtime_dependencies(resolver=resolver)
        if not status.available
    )