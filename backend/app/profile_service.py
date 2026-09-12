"""Career profile extraction services for the CareerVoice API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol

from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    ProfileExtractionResult,
)


class SupportsProfileWorkflow(Protocol):
    """Profile workflow operations required by the backend."""

    def extract_text_profile(
        self,
        *,
        career_preference_text: str,
        extractor: str,
        workspace: SessionWorkspace,
    ) -> ProfileExtractionResult:
        """Extract a structured profile from text."""
        ...


class SupportsProfileWorkflowFactory(Protocol):
    """Build a user-specific CareerVoice workflow."""

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> SupportsProfileWorkflow:
        """Return a workflow configured for one user and language."""
        ...


@dataclass(frozen=True)
class TextProfileExtraction:
    """Structured result returned by the backend profile service."""

    profile: dict[str, object]
    extractor: str
    output_language: str


class ProfileExtractionProvider(Protocol):
    """Provide career profile extraction for authenticated API users."""

    def extract_text(
        self,
        *,
        user: AppUser,
        career_preference_text: str,
        extractor: str,
        output_language: str,
    ) -> TextProfileExtraction:
        """Extract a structured career profile from text."""
        ...


@dataclass
class ProfileExtractionService:
    """Run profile extraction in an isolated temporary workspace."""

    workflow_factory: SupportsProfileWorkflowFactory
    temporary_root: Path | None = None

    def extract_text(
        self,
        *,
        user: AppUser,
        career_preference_text: str,
        extractor: str,
        output_language: str,
    ) -> TextProfileExtraction:
        """Extract a career profile from user-provided text."""
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
            prefix="careervoice-api-profile-",
            dir=temporary_root,
        ) as temporary_directory:
            workspace = SessionWorkspace.create(
                root_dir=temporary_directory,
            )

            result = workflow.extract_text_profile(
                career_preference_text=(
                    career_preference_text
                ),
                extractor=extractor,
                workspace=workspace,
            )

            profile = dict(
                result.review.profile
            )

        return TextProfileExtraction(
            profile=profile,
            extractor=result.extractor,
            output_language=output_language.strip(),
        )