from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from careervoice_ai_orchestrator.models import WorkflowConfig

from careervoice_ai_web_app.ai_usage import (
    AI_RANKING_AI_UNITS,
    DOCUMENT_RECOGNITION_AI_UNITS,
    PROFILE_EXTRACTION_AI_UNITS,
    VOICE_TRANSCRIPTION_AI_UNITS,
    SessionAIUsageBudget,
)
from careervoice_ai_web_app.document_input import (
    NoReadablePdfTextError,
    extract_document_text,
)
from careervoice_ai_web_app.document_recognition import (
    OpenAIDocumentRecognizer,
    RecognizedDocument,
)
from careervoice_ai_web_app.models import (
    JobSearchSettings,
    ProfileReview,
)
from careervoice_ai_web_app.orchestrator_gateway import (
    SupportsOrchestratorGateway,
)
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
    MAX_TRANSCRIPT_CHARACTERS,
    validate_job_search_limits,
    validate_recommendation_limit,
    validate_text_length,
)
from careervoice_ai_web_app.recommendation_models import (
    RecommendationDocument,
    RecommendationSettings,
)
from careervoice_ai_web_app.scanned_document import (
    RenderedDocumentPage,
    render_pdf_pages,
)
from careervoice_ai_web_app.session_workspace import SessionWorkspace
from careervoice_ai_web_app.voice_input import (
    SupportsVoiceTranscriber,
    VoiceTranscript,
    prepare_voice_recording,
)

SUPPORTED_PROFILE_EXTRACTORS = (
    "rules",
    "llm",
)


class SupportsDocumentRecognizer(Protocol):
    """Interface used for scanned-document text recognition."""

    def recognize(
        self,
        pages: Sequence[RenderedDocumentPage],
    ) -> RecognizedDocument:
        """Recognize text from rendered document pages."""


@dataclass(frozen=True)
class ProfileExtractionResult:
    """Result returned after extracting a text-based career profile."""

    workspace: SessionWorkspace
    review: ProfileReview
    extractor: str


@dataclass(frozen=True)
class ProfileConfirmationResult:
    """Result returned after saving a reviewed profile."""

    workspace: SessionWorkspace
    review: ProfileReview
    job_queries: tuple[str, ...]


@dataclass(frozen=True)
class JobSearchResult:
    """Result returned after collecting and deduplicating job listings."""

    workspace: SessionWorkspace
    settings: JobSearchSettings
    jobs: list[dict[str, object]]


@dataclass(frozen=True)
class RecommendationRunResult:
    """Result returned after ranking collected job listings."""

    workspace: SessionWorkspace
    settings: RecommendationSettings
    document: RecommendationDocument


class CareerVoiceWorkflowService:
    """UI-independent web workflow operations built on the Repo 4 gateway."""

    def __init__(
        self,
        gateway: SupportsOrchestratorGateway,
        *,
        document_recognizer: SupportsDocumentRecognizer | None = None,
        voice_transcriber: SupportsVoiceTranscriber | None = None,
        ai_usage_budget: SessionAIUsageBudget | None = None,
    ) -> None:
        self.gateway = gateway
        self._document_recognizer = document_recognizer
        self._voice_transcriber = voice_transcriber
        self._ai_usage_budget = ai_usage_budget

    def _reserve_ai_usage(
        self,
        units: int,
        *,
        feature: str,
    ) -> None:
        """Reserve session allowance when AI usage controls are enabled."""
        if self._ai_usage_budget is None:
            return

        self._ai_usage_budget.reserve(
            units,
            feature=feature,
        )

    def extract_text_profile(
        self,
        *,
        career_preference_text: str,
        extractor: str,
        workspace: SessionWorkspace,
    ) -> ProfileExtractionResult:
        """Extract a profile from text into one isolated session workspace."""
        validate_text_length(
            career_preference_text,
            field_name="Career information",
            max_characters=MAX_CAREER_TEXT_CHARACTERS,
        )

        cleaned_text = career_preference_text.strip()
        normalized_extractor = extractor.strip().lower()

        if not cleaned_text:
            raise ValueError("Career preference text cannot be empty.")

        if normalized_extractor not in SUPPORTED_PROFILE_EXTRACTORS:
            raise ValueError(
                "Unsupported profile extractor. Choose 'rules' or 'llm'."
            )

        if normalized_extractor == "llm":
            self._reserve_ai_usage(
                PROFILE_EXTRACTION_AI_UNITS,
                feature="AI-assisted profile creation",
            )

        workspace.ensure_exists()
        self._remove_downstream_outputs(workspace)

        config = self._build_config(
            workspace=workspace,
            input_mode="text",
            profile_extractor=normalized_extractor,
        )

        profile = self.gateway.extract_profile(
            config,
            profile_input_text=cleaned_text,
        )

        return ProfileExtractionResult(
            workspace=workspace,
            review=ProfileReview.from_profile(profile),
            extractor=normalized_extractor,
        )

    def transcribe_voice(
        self,
        *,
        filename: str,
        content: bytes,
        media_type: str,
    ) -> VoiceTranscript:
        """Convert a browser voice recording into reviewable text."""
        recording = prepare_voice_recording(
            filename=filename,
            content=content,
            media_type=media_type,
        )

        transcriber = self._voice_transcriber

        if transcriber is None:
            raise ValueError(
                "Voice transcription is not currently available."
            )

        self._reserve_ai_usage(
            VOICE_TRANSCRIPTION_AI_UNITS,
            feature="voice transcription",
        )

        transcript = transcriber.transcribe(
            recording
        )

        validate_text_length(
            transcript.text,
            field_name="Transcript",
            max_characters=MAX_TRANSCRIPT_CHARACTERS,
        )

        transcript_text = transcript.text.strip()

        if not transcript_text:
            raise ValueError(
                "No speech could be transcribed from the recording."
            )

        return VoiceTranscript(
            text=transcript_text,
        )

    def extract_voice_profile(
        self,
        *,
        filename: str,
        content: bytes,
        media_type: str,
        extractor: str,
        workspace: SessionWorkspace,
    ) -> ProfileExtractionResult:
        """Transcribe voice input and extract a career profile."""
        transcript = self.transcribe_voice(
            filename=filename,
            content=content,
            media_type=media_type,
        )

        return self.extract_text_profile(
            career_preference_text=transcript.text,
            extractor=extractor,
            workspace=workspace,
        )

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
        """Extract a career profile from an uploaded career document."""
        validate_text_length(
            additional_preferences,
            field_name="Additional preferences",
            max_characters=MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
        )

        try:
            document = extract_document_text(
                filename=filename,
                content=content,
            )
            document_text = document.text

        except NoReadablePdfTextError:
            document_text = self._recognize_image_based_pdf(
                content=content,
                allow_image_recognition=allow_image_recognition,
            )

        cleaned_preferences = additional_preferences.strip()

        combined_sections = [
            "Career background from uploaded document:",
            document_text,
        ]

        if cleaned_preferences:
            combined_sections.extend(
                [
                    "",
                    "Current career preferences:",
                    cleaned_preferences,
                ]
            )

        combined_text = "\n".join(combined_sections)

        return self.extract_text_profile(
            career_preference_text=combined_text,
            extractor=extractor,
            workspace=workspace,
        )

    def _recognize_image_based_pdf(
        self,
        *,
        content: bytes,
        allow_image_recognition: bool,
    ) -> str:
        """Recognize text from a scanned or image-only PDF."""
        if not allow_image_recognition:
            raise ValueError(
                "This PDF appears to contain scanned images rather than "
                "selectable text. Enable AI recognition for scanned PDFs "
                "and try again."
            )

        pages = render_pdf_pages(content)

        recognizer = self._document_recognizer

        if recognizer is None:
            try:
                recognizer = OpenAIDocumentRecognizer()
            except Exception as error:
                raise ValueError(
                    "Image-based document recognition is not currently "
                    "available."
                ) from error

        self._reserve_ai_usage(
            DOCUMENT_RECOGNITION_AI_UNITS,
            feature="scanned-document recognition",
        )

        recognized_document = recognizer.recognize(
            pages
        )

        return recognized_document.text

    def confirm_profile(
        self,
        *,
        profile: Mapping[str, object],
        profile_edits: Mapping[str, object],
        workspace: SessionWorkspace,
    ) -> ProfileConfirmationResult:
        """Save the reviewed profile and resolve profile-derived queries."""
        reviewed_profile = ProfileReview.from_profile(
            profile
        ).with_edits(profile_edits)

        self.gateway.save_career_profile(
            reviewed_profile.profile,
            workspace.profile_path,
        )

        self._remove_downstream_outputs(workspace)

        config = self._build_config(
            workspace=workspace,
            input_mode="profile",
        )

        job_queries = self.gateway.resolve_queries(config)

        return ProfileConfirmationResult(
            workspace=workspace,
            review=reviewed_profile,
            job_queries=job_queries,
        )

    def search_jobs(
        self,
        *,
        roles: Sequence[object],
        location: object,
        max_results_per_role: object,
        source: str,
        workspace: SessionWorkspace,
    ) -> JobSearchResult:
        """Collect jobs using explicit user-reviewed search settings."""
        settings = JobSearchSettings.from_values(
            roles=roles,
            location=location,
            max_results_per_role=max_results_per_role,
            source=source,
        )

        validate_job_search_limits(
            settings.roles,
            max_results=settings.max_results_per_role,
        )

        if not workspace.profile_path.is_file():
            raise ValueError(
                "Confirm your career profile before searching for jobs."
            )

        workspace.recommendations_output_path.unlink(
            missing_ok=True
        )

        config = self._build_config(
            workspace=workspace,
            input_mode="profile",
            job_source=settings.source,
            job_queries=settings.roles,
            job_location=settings.location,
            job_max_results=settings.max_results_per_role,
        )

        jobs = self.gateway.collect_jobs(config)

        return JobSearchResult(
            workspace=workspace,
            settings=settings,
            jobs=jobs,
        )

    def rank_jobs(
        self,
        *,
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        workspace: SessionWorkspace,
    ) -> RecommendationRunResult:
        """Rank collected jobs using validated recommendation settings."""
        settings = RecommendationSettings.from_values(
            scorer=scorer,
            max_results=max_results,
            exclude_rejected=exclude_rejected,
        )

        validate_recommendation_limit(
            settings.max_results
        )

        if not workspace.profile_path.is_file():
            raise ValueError(
                "Confirm your career profile before ranking jobs."
            )

        if not workspace.jobs_output_path.is_file():
            raise ValueError(
                "Search for jobs before generating recommendations."
            )

        if settings.scorer == "llm":
            self._reserve_ai_usage(
                AI_RANKING_AI_UNITS,
                feature="AI-assisted job ranking",
            )

        config = self._build_config(
            workspace=workspace,
            input_mode="profile",
            recommender_scorer=settings.scorer,
            recommendation_max_results=settings.max_results,
            exclude_rejected=settings.exclude_rejected,
        )

        recommendation_data = (
            self.gateway.generate_recommendations(config)
        )

        document = RecommendationDocument.from_mapping(
            recommendation_data
        )

        return RecommendationRunResult(
            workspace=workspace,
            settings=settings,
            document=document,
        )

    @staticmethod
    def _remove_downstream_outputs(
        workspace: SessionWorkspace,
    ) -> None:
        """Remove outputs that no longer match the current profile."""
        workspace.jobs_output_path.unlink(missing_ok=True)
        workspace.recommendations_output_path.unlink(
            missing_ok=True
        )

    @staticmethod
    def _build_config(
        *,
        workspace: SessionWorkspace,
        input_mode: str,
        profile_extractor: str = "rules",
        job_source: str = "adzuna",
        job_queries: tuple[str, ...] = (),
        job_location: str | None = None,
        job_max_results: int = 10,
        recommender_scorer: str = "rules",
        recommendation_max_results: int = 10,
        exclude_rejected: bool = False,
    ) -> WorkflowConfig:
        return WorkflowConfig(
            input_mode=input_mode,
            profile_input_path=workspace.profile_input_path,
            profile_path=workspace.profile_path,
            jobs_output_path=workspace.jobs_output_path,
            recommendations_output_path=(
                workspace.recommendations_output_path
            ),
            profile_extractor=profile_extractor,
            job_source=job_source,
            job_queries=job_queries,
            job_location=job_location,
            job_max_results=job_max_results,
            recommender_scorer=recommender_scorer,
            recommendation_max_results=(
                recommendation_max_results
            ),
            exclude_rejected=exclude_rejected,
        )
