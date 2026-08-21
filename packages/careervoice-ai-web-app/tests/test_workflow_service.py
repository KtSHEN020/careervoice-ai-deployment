from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import fitz
import pytest
from careervoice_ai_orchestrator.models import WorkflowConfig

from careervoice_ai_web_app.ai_usage import (
    AI_RANKING_AI_UNITS,
    AI_USAGE_UNITS_KEY,
    DOCUMENT_RECOGNITION_AI_UNITS,
    PROFILE_EXTRACTION_AI_UNITS,
    VOICE_TRANSCRIPTION_AI_UNITS,
    AIUsageLimitError,
    SessionAIUsageBudget,
)
from careervoice_ai_web_app.document_recognition import RecognizedDocument
from careervoice_ai_web_app.persistent_usage import UsageOperation
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
    MAX_RECOMMENDATIONS,
    MAX_TRANSCRIPT_CHARACTERS,
    PublicRequestLimitError,
)
from careervoice_ai_web_app.scanned_document import RenderedDocumentPage
from careervoice_ai_web_app.session_workspace import SessionWorkspace
from careervoice_ai_web_app.voice_input import (
    VoiceRecording,
    VoiceTranscript,
)
from careervoice_ai_web_app.workflow_service import (
    CareerVoiceWorkflowService,
)


def _create_image_only_pdf() -> bytes:
    document = fitz.open()

    page = document.new_page()

    pixmap = fitz.Pixmap(
        fitz.csRGB,
        (0, 0, 100, 100),
        0,
    )

    page.insert_image(
        page.rect,
        pixmap=pixmap,
    )

    content = document.tobytes()
    document.close()

    return content


class FakeDocumentRecognizer:
    def __init__(
        self,
        *,
        text: str = (
            "Alex Chen\n"
            "Junior Software Developer\n"
            "Python\n"
            "Adelaide"
        ),
    ) -> None:
        self.text = text
        self.calls: list[
            Sequence[RenderedDocumentPage]
        ] = []

    def recognize(
        self,
        pages: Sequence[RenderedDocumentPage],
    ) -> RecognizedDocument:
        self.calls.append(pages)

        return RecognizedDocument(
            text=self.text,
            page_count=len(pages),
            model="fake-model",
        )


class FakeVoiceTranscriber:
    def __init__(
        self,
        *,
        transcript: str = (
            "I want a junior backend developer role in Adelaide. "
            "I know Python and SQL and prefer hybrid work."
        ),
    ) -> None:
        self.transcript = transcript
        self.calls: list[VoiceRecording] = []

    def transcribe(
        self,
        recording: VoiceRecording,
    ) -> VoiceTranscript:
        self.calls.append(recording)

        return VoiceTranscript(
            text=self.transcript,
        )


class RecordingAIUsageBudget:
    def __init__(self) -> None:
        self.reservations: list[
            tuple[int, str, UsageOperation | None]
        ] = []

    def reserve(
        self,
        units: int,
        *,
        feature: str,
        operation: UsageOperation | None = None,
    ) -> None:
        self.reservations.append(
            (
                units,
                feature,
                operation,
            )
        )


class FakeOrchestratorGateway:
    def __init__(self) -> None:
        self.extract_profile_calls: list[
            tuple[WorkflowConfig, str | None]
        ] = []
        self.saved_profiles: list[
            tuple[dict[str, object], Path]
        ] = []
        self.resolve_query_calls: list[WorkflowConfig] = []
        self.collect_job_calls: list[WorkflowConfig] = []

        self.profile_to_return: dict[str, object] = {
            "target_roles": [
                "software developer",
                "backend developer",
            ],
            "skills": ["Python"],
        }

        self.jobs_to_return: list[dict[str, object]] = [
            {
                "job_id": "job-1",
                "title": "Junior Software Developer",
                "company": "Example Company",
                "location": "Adelaide",
            }
        ]

        self.generate_recommendation_calls: list[WorkflowConfig] = []

        self.recommendations_to_return: dict[str, object] = {
            "recommendations": [
                {
                    "job_id": "job-1",
                    "title": "Junior Software Developer",
                    "company": "Example Company",
                    "match_score": 84,
                    "recommendation_level": "strong_match",
                    "reasons": ["Matches the preferred role."],
                    "missing_skills": ["Docker"],
                    "penalties": [],
                    "uncertainties": [],
                    "is_rejected_by_constraints": False,
                    "scoring_method": "rules",
                }
            ],
            "total_jobs_scored": 1,
            "total_recommendations_returned": 1,
            "scoring_method": "rules",
        }

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        self.extract_profile_calls.append(
            (
                config,
                profile_input_text,
            )
        )

        return dict(self.profile_to_return)

    def save_career_profile(
        self,
        profile: Mapping[str, object],
        profile_path: str | Path,
    ) -> Path:
        path = Path(profile_path)
        profile_data = dict(profile)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            json.dumps(profile_data),
            encoding="utf-8",
        )

        self.saved_profiles.append(
            (
                profile_data,
                path,
            )
        )

        return path

    def resolve_queries(
        self,
        config: WorkflowConfig,
    ) -> tuple[str, ...]:
        self.resolve_query_calls.append(config)

        profile = json.loads(
            config.profile_path.read_text(
                encoding="utf-8",
            )
        )

        return tuple(profile["target_roles"])

    def collect_jobs(
        self,
        config: WorkflowConfig,
    ) -> list[dict[str, object]]:
        self.collect_job_calls.append(config)
        return list(self.jobs_to_return)

    def generate_recommendations(
        self,
        config: WorkflowConfig,
    ) -> dict[str, object]:
        self.generate_recommendation_calls.append(config)
        return dict(self.recommendations_to_return)


def test_extract_text_profile_uses_session_paths_and_selected_extractor(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    result = service.extract_text_profile(
        career_preference_text="  I want a software role.  ",
        extractor="llm",
        workspace=workspace,
    )

    config, profile_input_text = gateway.extract_profile_calls[0]

    assert profile_input_text == "I want a software role."
    assert config.input_mode == "text"
    assert config.profile_extractor == "llm"
    assert config.profile_input_path == workspace.profile_input_path
    assert config.profile_path == workspace.profile_path
    assert config.jobs_output_path == workspace.jobs_output_path
    assert (
        config.recommendations_output_path
        == workspace.recommendations_output_path
    )
    assert config.job_location is None

    assert result.extractor == "llm"
    assert result.review.target_roles == (
        "software developer",
        "backend developer",
    )


def test_extract_text_profile_rejects_blank_input_before_gateway_call(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        service.extract_text_profile(
            career_preference_text="   ",
            extractor="rules",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []


def test_extract_text_profile_rejects_unsupported_extractor(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported profile extractor",
    ):
        service.extract_text_profile(
            career_preference_text="I want a software role.",
            extractor="unsupported",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []


def test_new_profile_removes_stale_downstream_outputs(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.jobs_output_path.write_text(
        "stale jobs",
        encoding="utf-8",
    )
    workspace.recommendations_output_path.write_text(
        "stale recommendations",
        encoding="utf-8",
    )

    service.extract_text_profile(
        career_preference_text="I want a software role.",
        extractor="rules",
        workspace=workspace,
    )

    assert not workspace.jobs_output_path.exists()
    assert not workspace.recommendations_output_path.exists()


def test_confirm_profile_saves_edits_and_resolves_search_roles(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    original_profile = {
        "target_roles": ["software developer"],
        "skills": ["Python"],
        "experience_level": None,
        "preferred_locations": ["Adelaide"],
    }

    result = service.confirm_profile(
        profile=original_profile,
        profile_edits={
            "target_roles": [
                " junior backend developer ",
                "Python developer",
                "python developer",
            ],
            "skills": ["Python", "SQL"],
            "experience_level": "junior",
            "preferred_locations": ["Adelaide"],
            "preferred_work_types": ["hybrid"],
            "liked_areas": ["backend development"],
            "disliked_areas": ["sales"],
            "hard_constraints": ["not senior positions"],
            "career_goals": ["build backend experience"],
            "notes": ["Open to learning cloud tools"],
        },
        workspace=workspace,
    )

    assert result.review.profile == {
        "target_roles": [
            "junior backend developer",
            "Python developer",
        ],
        "skills": ["Python", "SQL"],
        "experience_level": "junior",
        "preferred_locations": ["Adelaide"],
        "preferred_work_types": ["hybrid"],
        "liked_areas": ["backend development"],
        "disliked_areas": ["sales"],
        "hard_constraints": ["not senior positions"],
        "career_goals": ["build backend experience"],
        "notes": ["Open to learning cloud tools"],
    }

    assert result.job_queries == (
        "junior backend developer",
        "Python developer",
    )


def test_confirm_profile_rejects_empty_roles_before_saving(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="At least one target role",
    ):
        service.confirm_profile(
            profile={
                "target_roles": ["software developer"],
            },
            profile_edits={
                "target_roles": ["", "  "],
            },
            workspace=workspace,
        )

    assert gateway.saved_profiles == []
    assert gateway.resolve_query_calls == []


def test_search_jobs_uses_explicit_web_settings(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )
    workspace.recommendations_output_path.write_text(
        "stale recommendations",
        encoding="utf-8",
    )

    result = service.search_jobs(
        roles=[
            " software developer ",
            "backend developer",
            "SOFTWARE DEVELOPER",
        ],
        location=" Adelaide ",
        max_results_per_role=5,
        source="adzuna",
        workspace=workspace,
    )

    config = gateway.collect_job_calls[0]

    assert config.job_queries == (
        "software developer",
        "backend developer",
    )
    assert config.job_location == "Adelaide"
    assert config.job_max_results == 5
    assert config.job_source == "adzuna"
    assert config.profile_path == workspace.profile_path
    assert config.jobs_output_path == workspace.jobs_output_path

    assert result.jobs == gateway.jobs_to_return
    assert result.settings.maximum_raw_results == 10
    assert not workspace.recommendations_output_path.exists()


def test_search_jobs_rejects_empty_roles_before_gateway_call(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="At least one role",
    ):
        service.search_jobs(
            roles=["", "  "],
            location="Adelaide",
            max_results_per_role=5,
            source="adzuna",
            workspace=workspace,
        )

    assert gateway.collect_job_calls == []


def test_search_jobs_requires_confirmed_profile_file(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Confirm your career profile",
    ):
        service.search_jobs(
            roles=["software developer"],
            location="Adelaide",
            max_results_per_role=5,
            source="adzuna",
            workspace=workspace,
        )

    assert gateway.collect_job_calls == []


def test_rank_jobs_uses_selected_recommendation_settings(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )
    workspace.jobs_output_path.write_text(
        "[]",
        encoding="utf-8",
    )

    result = service.rank_jobs(
        scorer="rules",
        max_results=5,
        exclude_rejected=True,
        workspace=workspace,
    )

    config = gateway.generate_recommendation_calls[0]

    assert config.recommender_scorer == "rules"
    assert config.recommendation_max_results == 5
    assert config.exclude_rejected is True
    assert config.profile_path == workspace.profile_path
    assert config.jobs_output_path == workspace.jobs_output_path
    assert (
        config.recommendations_output_path
        == workspace.recommendations_output_path
    )

    assert result.settings.scorer == "rules"
    assert result.document.total_recommendations_returned == 1


def test_rank_jobs_requires_confirmed_profile_file(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.jobs_output_path.write_text(
        "[]",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Confirm your career profile",
    ):
        service.rank_jobs(
            scorer="rules",
            max_results=5,
            exclude_rejected=False,
            workspace=workspace,
        )

    assert gateway.generate_recommendation_calls == []


def test_rank_jobs_requires_collected_jobs_file(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Search for jobs",
    ):
        service.rank_jobs(
            scorer="rules",
            max_results=5,
            exclude_rejected=False,
            workspace=workspace,
        )

    assert gateway.generate_recommendation_calls == []


def test_rank_jobs_rejects_invalid_settings_before_gateway_call(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported ranking method",
    ):
        service.rank_jobs(
            scorer="unsupported",
            max_results=5,
            exclude_rejected=False,
            workspace=workspace,
        )

    assert gateway.generate_recommendation_calls == []


def test_extract_document_profile_combines_document_and_preferences(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    result = service.extract_document_profile(
        filename="resume.txt",
        content=(
            b"Software Development Intern\n"
            b"Python\n"
            b"SQL\n"
            b"Git\n"
        ),
        additional_preferences=(
            "I want junior backend roles in Adelaide. "
            "I prefer hybrid work."
        ),
        extractor="llm",
        workspace=workspace,
    )

    config, profile_input_text = gateway.extract_profile_calls[0]

    assert profile_input_text == (
        "Career background from uploaded document:\n"
        "Software Development Intern\n"
        "Python\n"
        "SQL\n"
        "Git\n"
        "\n"
        "Current career preferences:\n"
        "I want junior backend roles in Adelaide. "
        "I prefer hybrid work."
    )

    assert config.input_mode == "text"
    assert config.profile_extractor == "llm"
    assert result.extractor == "llm"


def test_extract_document_profile_allows_document_without_preferences(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    service.extract_document_profile(
        filename="resume.txt",
        content=(
            b"Junior Software Developer\n"
            b"Python\n"
            b"Adelaide"
        ),
        additional_preferences="   ",
        extractor="rules",
        workspace=workspace,
    )

    _, profile_input_text = gateway.extract_profile_calls[0]

    assert profile_input_text == (
        "Career background from uploaded document:\n"
        "Junior Software Developer\n"
        "Python\n"
        "Adelaide"
    )


def test_extract_document_profile_rejects_invalid_document_before_gateway(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    service = CareerVoiceWorkflowService(gateway)
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported document type",
    ):
        service.extract_document_profile(
            filename="resume.doc",
            content=b"legacy document",
            additional_preferences="Backend roles",
            extractor="rules",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []


def test_extract_document_profile_recognizes_image_only_pdf(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    recognizer = FakeDocumentRecognizer()

    service = CareerVoiceWorkflowService(
        gateway,
        document_recognizer=recognizer,
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    result = service.extract_document_profile(
        filename="scanned-resume.pdf",
        content=_create_image_only_pdf(),
        additional_preferences=(
            "I prefer hybrid backend roles."
        ),
        extractor="llm",
        workspace=workspace,
        allow_image_recognition=True,
    )

    assert len(recognizer.calls) == 1

    _, profile_input_text = gateway.extract_profile_calls[0]

    assert "Alex Chen" in profile_input_text
    assert "Junior Software Developer" in profile_input_text
    assert "Python" in profile_input_text
    assert "Adelaide" in profile_input_text

    assert (
        "Current career preferences:\n"
        "I prefer hybrid backend roles."
        in profile_input_text
    )

    assert result.extractor == "llm"


def test_extract_document_profile_rejects_image_pdf_without_ai_access(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Enable AI recognition for scanned PDFs",
    ):
        service.extract_document_profile(
            filename="scanned-resume.pdf",
            content=_create_image_only_pdf(),
            additional_preferences="",
            extractor="rules",
            workspace=workspace,
            allow_image_recognition=False,
        )

    assert gateway.extract_profile_calls == []


def test_extract_voice_profile_transcribes_and_reuses_text_pipeline(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()
    transcriber = FakeVoiceTranscriber()

    service = CareerVoiceWorkflowService(
        gateway,
        voice_transcriber=transcriber,
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    result = service.extract_voice_profile(
        filename="career-voice.wav",
        content=b"fake-wav-content",
        media_type="audio/wav",
        extractor="llm",
        workspace=workspace,
    )

    assert len(transcriber.calls) == 1

    recording = transcriber.calls[0]

    assert recording.filename == "career-voice.wav"
    assert recording.media_type == "audio/wav"

    config, profile_input_text = (
        gateway.extract_profile_calls[0]
    )

    assert profile_input_text == (
        "I want a junior backend developer role in Adelaide. "
        "I know Python and SQL and prefer hybrid work."
    )

    assert config.input_mode == "text"
    assert config.profile_extractor == "llm"
    assert result.extractor == "llm"


def test_extract_voice_profile_requires_transcriber(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Voice transcription is not currently available",
    ):
        service.extract_voice_profile(
            filename="career-voice.wav",
            content=b"fake-wav-content",
            media_type="audio/wav",
            extractor="rules",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []


def test_extract_voice_profile_rejects_empty_transcript(
    tmp_path: Path,
) -> None:
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        voice_transcriber=FakeVoiceTranscriber(
            transcript="   "
        ),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="No speech could be transcribed",
    ):
        service.extract_voice_profile(
            filename="career-voice.wav",
            content=b"fake-wav-content",
            media_type="audio/wav",
            extractor="rules",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []


def test_transcribe_voice_returns_reviewable_transcript() -> None:
    transcriber = FakeVoiceTranscriber(
        transcript=(
            "I want a junior backend role in Adelaide."
        )
    )

    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
        voice_transcriber=transcriber,
    )

    result = service.transcribe_voice(
        filename="career-voice.wav",
        content=b"fake-wav-content",
        media_type="audio/wav",
    )

    assert result.text == (
        "I want a junior backend role in Adelaide."
    )

    assert len(transcriber.calls) == 1


def test_transcribe_voice_requires_transcriber() -> None:
    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway()
    )

    with pytest.raises(
        ValueError,
        match="Voice transcription is not currently available",
    ):
        service.transcribe_voice(
            filename="career-voice.wav",
            content=b"fake-wav-content",
            media_type="audio/wav",
        )


def test_llm_profile_extraction_reserves_ai_usage(
    tmp_path: Path,
) -> None:
    budget = RecordingAIUsageBudget()
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        ai_usage_budget=budget,
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    service.extract_text_profile(
        career_preference_text="I want a software role.",
        extractor="llm",
        workspace=workspace,
    )

    assert budget.reservations == [
        (
            PROFILE_EXTRACTION_AI_UNITS,
            "AI-assisted profile creation",
            UsageOperation.PROFILE_EXTRACTION,
        )
    ]


def test_rules_profile_extraction_does_not_use_ai_allowance(
    tmp_path: Path,
) -> None:
    state: dict[str, object] = {}
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        ai_usage_budget=SessionAIUsageBudget(
            state
        ),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    service.extract_text_profile(
        career_preference_text="I want a software role.",
        extractor="rules",
        workspace=workspace,
    )

    assert state.get(
        AI_USAGE_UNITS_KEY,
        0,
    ) == 0


def test_voice_transcription_reserves_ai_usage() -> None:
    budget = RecordingAIUsageBudget()

    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
        voice_transcriber=FakeVoiceTranscriber(),
        ai_usage_budget=budget,
    )

    service.transcribe_voice(
        filename="career-voice.wav",
        content=b"fake-wav-content",
        media_type="audio/wav",
    )

    assert budget.reservations == [
        (
            VOICE_TRANSCRIPTION_AI_UNITS,
            "voice transcription",
            UsageOperation.VOICE_TRANSCRIPTION,
        )
    ]


def test_scanned_document_recognition_reserves_ai_usage(
    tmp_path: Path,
) -> None:
    budget = RecordingAIUsageBudget()
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        document_recognizer=FakeDocumentRecognizer(),
        ai_usage_budget=budget,
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    service.extract_document_profile(
        filename="scanned-resume.pdf",
        content=_create_image_only_pdf(),
        additional_preferences="",
        extractor="rules",
        workspace=workspace,
        allow_image_recognition=True,
    )

    assert budget.reservations == [
        (
            DOCUMENT_RECOGNITION_AI_UNITS,
            "scanned-document recognition",
            UsageOperation.DOCUMENT_RECOGNITION,
        )
    ]


def test_llm_ranking_reserves_ai_usage(
    tmp_path: Path,
) -> None:
    budget = RecordingAIUsageBudget()
    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        ai_usage_budget=budget,
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )
    workspace.jobs_output_path.write_text(
        "[]",
        encoding="utf-8",
    )

    service.rank_jobs(
        scorer="llm",
        max_results=5,
        exclude_rejected=False,
        workspace=workspace,
    )

    assert budget.reservations == [
        (
            AI_RANKING_AI_UNITS,
            "AI-assisted job ranking",
            UsageOperation.AI_RANKING,
        )
    ]


def test_ai_usage_limit_blocks_ai_operation_before_gateway(
    tmp_path: Path,
) -> None:
    state: dict[str, object] = {
        AI_USAGE_UNITS_KEY: 20,
    }

    gateway = FakeOrchestratorGateway()

    service = CareerVoiceWorkflowService(
        gateway,
        ai_usage_budget=SessionAIUsageBudget(
            state
        ),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        AIUsageLimitError,
        match="AI-assisted profile creation",
    ):
        service.extract_text_profile(
            career_preference_text="I want a software role.",
            extractor="llm",
            workspace=workspace,
        )

    assert gateway.extract_profile_calls == []
    assert state[AI_USAGE_UNITS_KEY] == 20


def test_oversized_career_text_is_rejected_before_ai_usage(
    tmp_path: Path,
) -> None:
    state: dict[str, object] = {}

    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
        ai_usage_budget=SessionAIUsageBudget(
            state
        ),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Career information is too long",
    ):
        service.extract_text_profile(
            career_preference_text=(
                "a" * (MAX_CAREER_TEXT_CHARACTERS + 1)
            ),
            extractor="llm",
            workspace=workspace,
        )

    assert state.get(
        AI_USAGE_UNITS_KEY,
        0,
    ) == 0


def test_oversized_additional_preferences_are_rejected(
    tmp_path: Path,
) -> None:
    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Additional preferences is too long",
    ):
        service.extract_document_profile(
            filename="resume.txt",
            content=b"Python developer",
            additional_preferences=(
                "a"
                * (
                    MAX_ADDITIONAL_PREFERENCES_CHARACTERS
                    + 1
                )
            ),
            extractor="rules",
            workspace=workspace,
            allow_image_recognition=False,
        )


def test_search_jobs_rejects_too_many_queries(
    tmp_path: Path,
) -> None:
    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    roles = tuple(
        f"role-{index}"
        for index in range(MAX_JOB_QUERIES + 1)
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Too many job-search roles",
    ):
        service.search_jobs(
            roles=roles,
            location="Adelaide",
            max_results_per_role=1,
            source="adzuna",
            workspace=workspace,
        )


def test_search_jobs_rejects_too_many_results_per_query(
    tmp_path: Path,
) -> None:
    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Too many listings",
    ):
        service.search_jobs(
            roles=("software developer",),
            location="Adelaide",
            max_results_per_role=(
                MAX_JOB_RESULTS_PER_QUERY + 1
            ),
            source="adzuna",
            workspace=workspace,
        )


def test_excessive_recommendation_count_is_rejected_before_ai_usage(
    tmp_path: Path,
) -> None:
    state: dict[str, object] = {}

    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
        ai_usage_budget=SessionAIUsageBudget(
            state
        ),
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )
    workspace.jobs_output_path.write_text(
        "[]",
        encoding="utf-8",
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Too many recommendations",
    ):
        service.rank_jobs(
            scorer="llm",
            max_results=MAX_RECOMMENDATIONS + 1,
            exclude_rejected=False,
            workspace=workspace,
        )

    assert state.get(
        AI_USAGE_UNITS_KEY,
        0,
    ) == 0


def test_oversized_voice_transcript_is_rejected() -> None:
    class LongTranscriptTranscriber:
        def transcribe(
            self,
            recording: VoiceRecording,
        ) -> VoiceTranscript:
            return VoiceTranscript(
                text=(
                    "a"
                    * (
                        MAX_TRANSCRIPT_CHARACTERS
                        + 1
                    )
                )
            )

    state: dict[str, object] = {}

    service = CareerVoiceWorkflowService(
        FakeOrchestratorGateway(),
        voice_transcriber=LongTranscriptTranscriber(),
        ai_usage_budget=SessionAIUsageBudget(
            state
        ),
    )

    with pytest.raises(
        PublicRequestLimitError,
        match="Transcript is too long",
    ):
        service.transcribe_voice(
            filename="career-voice.wav",
            content=b"fake-wav-content",
            media_type="audio/wav",
        )