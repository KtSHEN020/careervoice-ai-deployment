"""Recommendation services for the CareerVoice API."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from job_listing_collector.models import NormalizedJob

from careervoice_ai_web_app.recommendation_models import (
    RecommendationDocument,
    RecommendationSettings,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    ProfileConfirmationResult,
    RecommendationRunResult,
)


class SupportsRecommendationWorkflow(Protocol):
    """CareerVoice workflow operations required for recommendation."""

    def confirm_profile(
        self,
        *,
        profile: Mapping[str, object],
        profile_edits: Mapping[str, object],
        workspace: SessionWorkspace,
    ) -> ProfileConfirmationResult:
        """Validate and save a reviewed career profile."""
        ...

    def rank_jobs(
        self,
        *,
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        workspace: SessionWorkspace,
    ) -> RecommendationRunResult:
        """Rank jobs using the existing CareerVoice workflow."""
        ...


class SupportsRecommendationWorkflowFactory(Protocol):
    """Build a user-specific recommendation workflow."""

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> SupportsRecommendationWorkflow:
        """Return one CareerVoice workflow."""
        ...


@dataclass(frozen=True)
class RecommendationExecution:
    """Result returned by the backend recommendation service."""

    settings: RecommendationSettings
    document: RecommendationDocument
    output_language: str


class RecommendationProvider(Protocol):
    """Provide recommendations for authenticated API users."""

    def recommend(
        self,
        *,
        user: AppUser,
        profile: Mapping[str, object],
        jobs: Sequence[Mapping[str, object]],
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        output_language: str,
    ) -> RecommendationExecution:
        """Generate recommendations from a reviewed profile and jobs."""
        ...


@dataclass
class RecommendationService:
    """Run recommendation generation in an isolated workspace."""

    workflow_factory: SupportsRecommendationWorkflowFactory
    temporary_root: Path | None = None

    def recommend(
        self,
        *,
        user: AppUser,
        profile: Mapping[str, object],
        jobs: Sequence[Mapping[str, object]],
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        output_language: str,
    ) -> RecommendationExecution:
        """Generate recommendations from user-reviewed inputs."""
        workflow = self.workflow_factory(
            user=user,
            output_language=output_language,
        )

        normalized_jobs = [
            NormalizedJob.model_validate(
                job
            ).to_repo2_dict()
            for job in jobs
        ]

        if not normalized_jobs:
            raise ValueError(
                "At least one job is required to generate recommendations."
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
            prefix="careervoice-api-recommendations-",
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

            workspace.jobs_output_path.write_text(
                json.dumps(
                    normalized_jobs,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = workflow.rank_jobs(
                scorer=scorer,
                max_results=max_results,
                exclude_rejected=exclude_rejected,
                workspace=workspace,
            )

        return RecommendationExecution(
            settings=result.settings,
            document=result.document,
            output_language=output_language.strip(),
        )