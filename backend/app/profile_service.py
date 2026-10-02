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

from careervoice_ai_web_app.voice_input import (
    VoiceTranscript,
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

    def extract_document_profile(
        self,
        *,
        filename: str,
        content: bytes,
        additional_preferences: str,
        extractor: str,
        workspace: SessionWorkspace,
        allow_image_recognition: bool = False,
    ) -> ProfileExtractionResult:
        """Extract a structured profile from a career document."""
        ...

    def transcribe_voice(
        self,
        *,
        filename: str,
        content: bytes,
        media_type: str,
    ) -> VoiceTranscript:
        """Transcribe one browser voice recording."""
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

    def extract_document(
        self,
        *,
        user: AppUser,
        filename: str,
        content: bytes,
        additional_preferences: str,
        extractor: str,
        output_language: str,
        allow_image_recognition: bool = False,
    ) -> TextProfileExtraction:
        """Extract a structured career profile from a document."""
        ...

    def transcribe_voice(
        self,
        *,
        user: AppUser,
        filename: str,
        content: bytes,
        media_type: str,
        output_language: str,
    ) -> VoiceTranscript:
        """Transcribe authenticated browser voice input."""
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

        with self._workspace() as workspace:
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

    def extract_document(
        self,
        *,
        user: AppUser,
        filename: str,
        content: bytes,
        additional_preferences: str,
        extractor: str,
        output_language: str,
        allow_image_recognition: bool = False,
    ) -> TextProfileExtraction:
        """Extract a career profile from an uploaded document."""
        workflow = self.workflow_factory(
            user=user,
            output_language=output_language,
        )

        with self._workspace() as workspace:
            result = workflow.extract_document_profile(
                filename=filename,
                content=content,
                additional_preferences=(
                    additional_preferences
                ),
                extractor=extractor,
                workspace=workspace,
                allow_image_recognition=(
                    allow_image_recognition
                ),
            )

            profile = dict(
                result.review.profile
            )

        return TextProfileExtraction(
            profile=profile,
            extractor=result.extractor,
            output_language=output_language.strip(),
        )

    def transcribe_voice(
        self,
        *,
        user: AppUser,
        filename: str,
        content: bytes,
        media_type: str,
        output_language: str,
    ) -> VoiceTranscript:
        """Transcribe browser voice input for one authenticated user."""
        workflow = self.workflow_factory(
            user=user,
            output_language=output_language,
        )

        return workflow.transcribe_voice(
            filename=filename,
            content=content,
            media_type=media_type,
        )

    def _workspace(
        self,
    ) -> _TemporaryProfileWorkspace:
        """Create one isolated temporary profile workspace."""
        return _TemporaryProfileWorkspace(
            temporary_root=self.temporary_root,
        )


class _TemporaryProfileWorkspace:
    """Context manager for one temporary CareerVoice workspace."""

    def __init__(
        self,
        *,
        temporary_root: Path | None,
    ) -> None:
        self._temporary_root = temporary_root
        self._temporary_directory: (
            TemporaryDirectory[str] | None
        ) = None

    def __enter__(
        self,
    ) -> SessionWorkspace:
        temporary_root: str | None = None

        if self._temporary_root is not None:
            self._temporary_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            temporary_root = str(
                self._temporary_root
            )

        self._temporary_directory = (
            TemporaryDirectory(
                prefix="careervoice-api-profile-",
                dir=temporary_root,
            )
        )

        return SessionWorkspace.create(
            root_dir=self._temporary_directory.name,
        )

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        if self._temporary_directory is not None:
            self._temporary_directory.cleanup()