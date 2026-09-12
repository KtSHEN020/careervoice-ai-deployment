from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.public_limits import (
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