from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.main import create_app
from backend.app.security import (
    CurrentUserAccessDeniedError,
    InvalidAccessTokenError,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


@dataclass
class FakeCurrentUserResolver:
    expected_token: str
    user: AppUser

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        if access_token == "forbidden-test-token":
            raise CurrentUserAccessDeniedError(
                "CareerVoice access is denied."
            )

        if access_token != self.expected_token:
            raise InvalidAccessTokenError(
                "Access token is invalid."
            )

        return self.user


def create_test_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def create_test_client() -> TestClient:
    resolver = FakeCurrentUserResolver(
        expected_token="valid-test-token",
        user=create_test_user(),
    )

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=resolver,
    )

    return TestClient(app)


def test_me_requires_authentication() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/me",
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_rejects_invalid_access_token() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_me_rejects_unauthorized_careervoice_user() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer forbidden-test-token",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "CareerVoice access is not permitted."
    }


def test_me_returns_authenticated_user() -> None:
    client = create_test_client()

    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer valid-test-token",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(TEST_USER_ID),
        "email": "tester@example.com",
        "enabled": True,
    }


def test_me_fails_closed_when_auth_is_unconfigured() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
        )
    )
    client = TestClient(app)

    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer any-token",
        },
    )

    assert response.status_code == 503