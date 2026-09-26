from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.main import create_app
from backend.app.security import (
    InvalidAccessTokenError,
)
from backend.app.usage_service import (
    DailyUsageStatus,
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


@dataclass
class FakeDailyUsageStatusProvider:
    status: DailyUsageStatus

    user_seen: AppUser | None = None

    def get_status(
        self,
        user: AppUser,
    ) -> DailyUsageStatus:
        self.user_seen = user
        return self.status


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def create_usage_status() -> DailyUsageStatus:
    return DailyUsageStatus(
        usage_date=date(2026, 9, 12),
        daily_ai_unit_limit=40,
        ai_quota_exempt=False,
        ai_units_used=11,
        remaining_ai_units=29,
        ai_profile_extractions=1,
        voice_transcriptions=0,
        document_recognitions=0,
        ai_ranking_runs=1,
        job_searches=3,
    )


def test_usage_requires_authentication() -> None:
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
        daily_usage_status_provider=(
            FakeDailyUsageStatusProvider(
                status=create_usage_status()
            )
        ),
    )

    client = TestClient(app)

    response = client.get(
        "/api/v1/usage"
    )

    assert response.status_code == 401


def test_usage_returns_current_users_daily_status() -> None:
    user = create_user()

    usage_provider = (
        FakeDailyUsageStatusProvider(
            status=create_usage_status()
        )
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
        daily_usage_status_provider=usage_provider,
    )

    client = TestClient(app)

    response = client.get(
        "/api/v1/usage",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "usage_date": "2026-09-12",
        "daily_ai_unit_limit": 40,
        "ai_quota_exempt": False,
        "ai_units_used": 11,
        "remaining_ai_units": 29,
        "ai_profile_extractions": 1,
        "voice_transcriptions": 0,
        "document_recognitions": 0,
        "ai_ranking_runs": 1,
        "job_searches": 3,
    }

    assert usage_provider.user_seen is user


def test_usage_rejects_invalid_access_token() -> None:
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
        daily_usage_status_provider=(
            FakeDailyUsageStatusProvider(
                status=create_usage_status()
            )
        ),
    )

    client = TestClient(app)

    response = client.get(
        "/api/v1/usage",
        headers={
            "Authorization": (
                "Bearer invalid-test-token"
            ),
        },
    )

    assert response.status_code == 401


def test_usage_fails_closed_when_service_is_unconfigured() -> None:
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

    response = client.get(
        "/api/v1/usage",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Usage service is unavailable."
    }


def test_usage_returns_unlimited_status_for_quota_exempt_user() -> None:
    user = AppUser(
        id=TEST_USER_ID,
        email="admin@example.com",
        auth_provider="supabase",
        auth_subject="provider-admin-123",
        enabled=True,
        ai_quota_exempt=True,
    )

    usage_provider = FakeDailyUsageStatusProvider(
        status=DailyUsageStatus(
            usage_date=date(2026, 9, 12),
            daily_ai_unit_limit=40,
            ai_quota_exempt=True,
            ai_units_used=75,
            remaining_ai_units=None,
            ai_profile_extractions=5,
            voice_transcriptions=2,
            document_recognitions=1,
            ai_ranking_runs=6,
            job_searches=8,
        )
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
        daily_usage_status_provider=usage_provider,
    )

    client = TestClient(app)

    response = client.get(
        "/api/v1/usage",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
    )

    assert response.status_code == 200

    assert response.json()[
        "ai_quota_exempt"
    ] is True

    assert response.json()[
        "ai_units_used"
    ] == 75

    assert response.json()[
        "remaining_ai_units"
    ] is None