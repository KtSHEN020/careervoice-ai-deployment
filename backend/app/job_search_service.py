"""Job-search services for the CareerVoice API."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from careervoice_ai_web_app.models import (
    JobSearchSettings,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    JobSearchResult,
    ProfileConfirmationResult,
)


class SupportsJobSearchWorkflow(Protocol):
    """CareerVoice workflow operations required for job searching."""

    def confirm_profile(
        self,
        *,
        profile: Mapping[str, object],
        profile_edits: Mapping[str, object],
        workspace: SessionWorkspace,
    ) -> ProfileConfirmationResult:
        """Validate and save a reviewed career profile."""
        ...

    def search_jobs(
        self,
        *,
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str,
        workspace: SessionWorkspace,
    ) -> JobSearchResult:
        """Search for jobs using reviewed settings."""
        ...


class SupportsJobSearchWorkflowFactory(Protocol):
    """Build a user-specific workflow for job searching."""

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> SupportsJobSearchWorkflow:
        """Return one CareerVoice workflow."""
        ...


class SupportsJobSearchUsageRecorder(Protocol):
    """Record successful CareerVoice job searches."""

    def record_job_search(
        self,
        *,
        user: AppUser,
    ) -> None:
        """Record one successful job search."""
        ...


@dataclass(frozen=True)
class JobSearchExecution:
    """Result returned by the backend job-search service."""

    settings: JobSearchSettings
    jobs: list[dict[str, object]]
    output_language: str


class JobSearchProvider(Protocol):
    """Provide job searching for authenticated API users."""

    def search(
        self,
        *,
        user: AppUser,
        profile: Mapping[str, object],
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str,
        output_language: str,
    ) -> JobSearchExecution:
        """Search for jobs using a reviewed career profile."""
        ...


@dataclass
class JobSearchService:
    """Run job searching in an isolated temporary workspace."""

    workflow_factory: SupportsJobSearchWorkflowFactory
    usage_recorder: SupportsJobSearchUsageRecorder
    temporary_root: Path | None = None

    def search(
        self,
        *,
        user: AppUser,
        profile: Mapping[str, object],
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str,
        output_language: str,
    ) -> JobSearchExecution:
        """Search for jobs using a reviewed career profile."""
        workflow = self.workflow_factory(
            user=user,
            output_language=output_language,
        )

        temporary_root: str | None = None

        if self.temporary_root is not None:
            self.temporary_root.mkdir(
                parents=True,
                exist_ok=True,
            )
            temporary_root = str(
                self.temporary_root
            )

        with TemporaryDirectory(
            prefix="careervoice-api-jobs-",
            dir=temporary_root,
        ) as temporary_directory:
            workspace = SessionWorkspace.create(
                root_dir=temporary_directory,
            )

            workflow.confirm_profile(
                profile=profile,
                profile_edits={},
                workspace=workspace,
            )

            result = workflow.search_jobs(
                roles=roles,
                location=location,
                max_results_per_role=(
                    max_results_per_role
                ),
                source=source,
                workspace=workspace,
            )

            jobs = [
                dict(job)
                for job in result.jobs
            ]

        self.usage_recorder.record_job_search(
            user=user
        )

        return JobSearchExecution(
            settings=result.settings,
            jobs=jobs,
            output_language=output_language.strip(),
        )