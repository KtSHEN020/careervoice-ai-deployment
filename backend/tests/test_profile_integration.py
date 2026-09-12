from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.main import create_app
from backend.app.profile_runtime import (
    CareerVoiceProfileWorkflowFactory,
)
from backend.app.profile_service import (
    ProfileExtractionService,
)
from backend.app.security import (
    InvalidAccessTokenError,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


class FakeCurrentUserResolver:
    def __init__(
        self,
        user: AppUser,
    ) -> None:
        self.user = user

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        if access_token != "valid-test-token":
            raise InvalidAccessTokenError(
                "Access token is invalid."
            )

        return self.user


class FakeUsageRepository:
    def __init__(self) -> None:
        self.consume_calls: list[
            dict[str, object]
        ] = []

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        return DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=0,
            ai_profile_extractions=0,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=0,
        )

    def consume(
        self,
        *,
        user: AppUser,
        usage_date: date,
        units: int,
        daily_limit: int,
        operation: UsageOperation,
    ) -> UsageDecision:
        self.consume_calls.append(
            {
                "user": user,
                "usage_date": usage_date,
                "units": units,
                "daily_limit": daily_limit,
                "operation": operation,
            }
        )

        return UsageDecision(
            allowed=True,
            ai_units_used=units,
            remaining_ai_units=(
                daily_limit - units
            ),
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_profile_api_reaches_real_rule_based_extractor() -> None:
    user = create_user()
    usage_repository = FakeUsageRepository()

    workflow_factory = (
        CareerVoiceProfileWorkflowFactory(
            usage_repository=usage_repository,
            daily_ai_unit_limit=40,
        )
    )

    profile_service = ProfileExtractionService(
        workflow_factory=workflow_factory
    )

    app = create_app(
        settings=BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        profile_extraction_provider=(
            profile_service
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
                "I am a junior software developer "
                "with Python experience. "
                "I want a software developer role "
                "in Adelaide with hybrid work."
            ),
            "extractor": "rules",
            "output_language": "en",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["extractor"] == "rules"
    assert body["output_language"] == "en"

    assert isinstance(
        body["profile"]["target_roles"],
        list,
    )
    assert isinstance(
        body["profile"]["skills"],
        list,
    )
    assert isinstance(
        body["profile"]["preferred_locations"],
        list,
    )

    assert usage_repository.consume_calls == []