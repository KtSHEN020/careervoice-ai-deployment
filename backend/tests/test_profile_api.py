from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.document_input import (
    MAX_DOCUMENT_BYTES,
)
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.profile_service import (
    TextProfileExtraction,
)
from backend.app.security import (
    InvalidAccessTokenError,
)
from backend.app.main import (
    create_app,
    create_runtime_app,
)

from careervoice_ai_web_app.voice_input import (
    MAX_VOICE_RECORDING_BYTES,
    VoiceTranscript,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


@dataclass
class FakeCurrentUserResolver:
    user: AppUser

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        if access_token != "valid-test-token":
            raise InvalidAccessTokenError(
                "Access token is invalid."
            )

        return self.user


class FakeProfileExtractionProvider:
    def __init__(
        self,
        *,
        quota_exhausted: bool = False,
    ) -> None:
        self.quota_exhausted = quota_exhausted
        self.calls: list[
            dict[str, object]
        ] = []
        self.document_calls: list[
            dict[str, object]
        ] = []
        self.voice_calls: list[
            dict[str, object]
        ] = []

    def extract_text(
        self,
        *,
        user: AppUser,
        career_preference_text: str,
        extractor: str,
        output_language: str,
    ) -> TextProfileExtraction:
        self.calls.append(
            {
                "user": user,
                "career_preference_text": (
                    career_preference_text
                ),
                "extractor": extractor,
                "output_language": (
                    output_language
                ),
            }
        )

        if self.quota_exhausted:
            raise AIUsageLimitError(
                "No allowance remains."
            )

        return TextProfileExtraction(
            profile={
                "target_roles": [
                    "backend developer",
                ],
                "skills": [
                    "Python",
                ],
                "experience_level": "junior",
                "preferred_locations": [
                    "Adelaide",
                ],
                "preferred_work_types": [
                    "hybrid",
                ],
                "liked_areas": [
                    "backend development",
                ],
                "disliked_areas": [],
                "hard_constraints": [],
                "career_goals": [],
                "notes": [],
            },
            extractor=extractor,
            output_language=output_language,
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
        self.document_calls.append(
            {
                "user": user,
                "filename": filename,
                "content": content,
                "additional_preferences": (
                    additional_preferences
                ),
                "extractor": extractor,
                "output_language": (
                    output_language
                ),
                "allow_image_recognition": (
                    allow_image_recognition
                ),
            }
        )

        if self.quota_exhausted:
            raise AIUsageLimitError(
                "No allowance remains."
            )

        return TextProfileExtraction(
            profile={
                "target_roles": [
                    "backend developer",
                ],
                "skills": [
                    "Python",
                ],
                "experience_level": "junior",
                "preferred_locations": [
                    "Adelaide",
                ],
                "preferred_work_types": [
                    "hybrid",
                ],
                "liked_areas": [
                    "backend development",
                ],
                "disliked_areas": [],
                "hard_constraints": [],
                "career_goals": [],
                "notes": [],
            },
            extractor=extractor,
            output_language=output_language,
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
        self.voice_calls.append(
            {
                "user": user,
                "filename": filename,
                "content": content,
                "media_type": media_type,
                "output_language": output_language,
            }
        )

        if self.quota_exhausted:
            raise AIUsageLimitError(
                "No allowance remains."
            )

        return VoiceTranscript(
            text=(
                "I am a junior Python developer "
                "looking for backend roles in Adelaide."
            )
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_profile_extraction_requires_authentication() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        json={
            "career_preference_text": (
                "I want a backend role."
            ),
            "extractor": "rules",
            "output_language": "en",
        },
    )

    assert response.status_code == 401
    assert provider.calls == []


def test_profile_extraction_returns_structured_profile() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "I want a junior backend role."
            ),
            "extractor": "llm",
            "output_language": "zh-CN",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "profile": {
            "target_roles": [
                "backend developer",
            ],
            "skills": [
                "Python",
            ],
            "experience_level": "junior",
            "preferred_locations": [
                "Adelaide",
            ],
            "preferred_work_types": [
                "hybrid",
            ],
            "liked_areas": [
                "backend development",
            ],
            "disliked_areas": [],
            "hard_constraints": [],
            "career_goals": [],
            "notes": [],
        },
        "extractor": "llm",
        "output_language": "zh-CN",
    }

    assert provider.calls == [
        {
            "user": user,
            "career_preference_text": (
                "I want a junior backend role."
            ),
            "extractor": "llm",
            "output_language": "zh-CN",
        }
    ]


def test_profile_extraction_rejects_invalid_extractor() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "I want a backend role."
            ),
            "extractor": "unknown",
            "output_language": "en",
        },
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_profile_extraction_enforces_text_limit() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "x"
                * (
                    MAX_CAREER_TEXT_CHARACTERS
                    + 1
                )
            ),
            "extractor": "rules",
            "output_language": "en",
        },
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_profile_extraction_returns_429_when_ai_quota_is_exhausted() -> None:
    user = create_user()

    provider = FakeProfileExtractionProvider(
        quota_exhausted=True
    )

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "I want a backend role."
            ),
            "extractor": "llm",
            "output_language": "en",
        },
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": (
            "Daily AI allowance is insufficient "
            "for this request."
        )
    }


def test_profile_extraction_fails_closed_when_service_is_unconfigured() -> None:
    user = create_user()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "I want a backend role."
            ),
            "extractor": "rules",
            "output_language": "en",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "Profile extraction service is unavailable."
        )
    }


def test_runtime_profile_endpoint_fails_closed_without_configuration() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract",
        headers={
            "Authorization": (
                "Bearer fake-test-token"
            ),
        },
        json={
            "career_preference_text": (
                "I want a backend role."
            ),
            "extractor": "rules",
            "output_language": "en",
        },
    )

    assert response.status_code == 503


def test_document_profile_extraction_requires_authentication() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract-document",
        data={
            "extractor": "rules",
            "output_language": "en",
        },
        files={
            "document": (
                "resume.txt",
                b"Python developer",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 401
    assert provider.document_calls == []


def test_document_profile_extraction_returns_structured_profile() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract-document",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "extractor": "llm",
            "output_language": "zh-CN",
            "additional_preferences": (
                "I want backend roles in Adelaide."
            ),
            "allow_image_recognition": "true",
        },
        files={
            "document": (
                "resume.pdf",
                b"fake-pdf-content",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "profile": {
            "target_roles": [
                "backend developer",
            ],
            "skills": [
                "Python",
            ],
            "experience_level": "junior",
            "preferred_locations": [
                "Adelaide",
            ],
            "preferred_work_types": [
                "hybrid",
            ],
            "liked_areas": [
                "backend development",
            ],
            "disliked_areas": [],
            "hard_constraints": [],
            "career_goals": [],
            "notes": [],
        },
        "extractor": "llm",
        "output_language": "zh-CN",
    }

    assert provider.document_calls == [
        {
            "user": user,
            "filename": "resume.pdf",
            "content": b"fake-pdf-content",
            "additional_preferences": (
                "I want backend roles in Adelaide."
            ),
            "extractor": "llm",
            "output_language": "zh-CN",
            "allow_image_recognition": True,
        }
    ]


def test_document_profile_extraction_rejects_oversized_upload() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract-document",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "extractor": "rules",
            "output_language": "en",
        },
        files={
            "document": (
                "resume.txt",
                b"x" * (MAX_DOCUMENT_BYTES + 1),
                "text/plain",
            ),
        },
    )

    assert response.status_code == 413

    assert response.json() == {
        "detail": (
            "The uploaded document is too large. "
            "The maximum supported size is 5 MB."
        )
    }

    assert provider.document_calls == []


def test_document_profile_extraction_enforces_preferences_limit() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract-document",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "extractor": "rules",
            "output_language": "en",
            "additional_preferences": (
                "x"
                * (
                    MAX_ADDITIONAL_PREFERENCES_CHARACTERS
                    + 1
                )
            ),
        },
        files={
            "document": (
                "resume.txt",
                b"Python developer",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 422
    assert provider.document_calls == []


def test_document_profile_extraction_returns_429_when_ai_quota_is_exhausted() -> None:
    user = create_user()

    provider = FakeProfileExtractionProvider(
        quota_exhausted=True
    )

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/extract-document",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "extractor": "llm",
            "output_language": "en",
        },
        files={
            "document": (
                "resume.txt",
                b"Python developer",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": (
            "Daily AI allowance is insufficient "
            "for this request."
        )
    }


def test_voice_transcription_requires_authentication() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/transcribe-voice",
        data={
            "output_language": "en",
        },
        files={
            "recording": (
                "career-voice.mp4",
                b"fake-browser-audio",
                "audio/mp4",
            ),
        },
    )

    assert response.status_code == 401
    assert provider.voice_calls == []


def test_voice_transcription_returns_transcript() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/transcribe-voice",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "output_language": "en",
        },
        files={
            "recording": (
                "career-voice.mp4",
                b"fake-browser-audio",
                "audio/mp4",
            ),
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "text": (
            "I am a junior Python developer "
            "looking for backend roles in Adelaide."
        )
    }

    assert provider.voice_calls == [
        {
            "user": user,
            "filename": "career-voice.mp4",
            "content": b"fake-browser-audio",
            "media_type": "audio/mp4",
            "output_language": "en",
        }
    ]


def test_voice_transcription_rejects_oversized_recording() -> None:
    user = create_user()
    provider = FakeProfileExtractionProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/transcribe-voice",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "output_language": "en",
        },
        files={
            "recording": (
                "career-voice.mp4",
                b"x"
                * (
                    MAX_VOICE_RECORDING_BYTES
                    + 1
                ),
                "audio/mp4",
            ),
        },
    )

    assert response.status_code == 413

    assert response.json() == {
        "detail": (
            "The voice recording is too large. "
            "The maximum supported size is 10 MB."
        )
    }

    assert provider.voice_calls == []


def test_voice_transcription_returns_429_when_ai_quota_is_exhausted() -> None:
    user = create_user()

    provider = FakeProfileExtractionProvider(
        quota_exhausted=True
    )

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/profile/transcribe-voice",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        data={
            "output_language": "en",
        },
        files={
            "recording": (
                "career-voice.webm",
                b"fake-browser-audio",
                "audio/webm",
            ),
        },
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": (
            "Daily AI allowance is insufficient "
            "for this request."
        )
    }