from dataclasses import FrozenInstanceError

import pytest

from careervoice_ai_web_app.authentication import (
    AuthenticationSession,
)
from careervoice_ai_web_app.user_models import AuthenticatedIdentity


def _identity() -> AuthenticatedIdentity:
    return AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )


def test_authentication_session_stores_identity() -> None:
    identity = _identity()

    session = AuthenticationSession(
        identity=identity,
        access_token="access-token",
    )

    assert session.identity is identity


def test_authentication_session_normalizes_access_token() -> None:
    session = AuthenticationSession(
        identity=_identity(),
        access_token="  access-token  ",
    )

    assert session.access_token == "access-token"


def test_authentication_session_normalizes_refresh_token() -> None:
    session = AuthenticationSession(
        identity=_identity(),
        access_token="access-token",
        refresh_token="  refresh-token  ",
    )

    assert session.refresh_token == "refresh-token"


def test_authentication_session_allows_missing_refresh_token() -> None:
    session = AuthenticationSession(
        identity=_identity(),
        access_token="access-token",
    )

    assert session.refresh_token is None


def test_authentication_session_allows_expiry_timestamp() -> None:
    session = AuthenticationSession(
        identity=_identity(),
        access_token="access-token",
        expires_at=1_800_000_000,
    )

    assert session.expires_at == 1_800_000_000


@pytest.mark.parametrize(
    "access_token",
    [
        "",
        "   ",
    ],
)
def test_authentication_session_rejects_empty_access_token(
    access_token: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="Access token cannot be empty",
    ):
        AuthenticationSession(
            identity=_identity(),
            access_token=access_token,
        )


def test_authentication_session_rejects_non_text_access_token() -> None:
    with pytest.raises(
        ValueError,
        match="Access token must be text",
    ):
        AuthenticationSession(
            identity=_identity(),
            access_token=123,  # type: ignore[arg-type]
        )


def test_authentication_session_rejects_empty_refresh_token() -> None:
    with pytest.raises(
        ValueError,
        match="Refresh token cannot be empty",
    ):
        AuthenticationSession(
            identity=_identity(),
            access_token="access-token",
            refresh_token="   ",
        )


@pytest.mark.parametrize(
    "expires_at",
    [
        -1,
        1.5,
        True,
    ],
)
def test_authentication_session_rejects_invalid_expiry(
    expires_at: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="Session expiry must be a non-negative integer",
    ):
        AuthenticationSession(
            identity=_identity(),
            access_token="access-token",
            expires_at=expires_at,  # type: ignore[arg-type]
        )


def test_authentication_session_is_immutable() -> None:
    session = AuthenticationSession(
        identity=_identity(),
        access_token="access-token",
    )

    with pytest.raises(FrozenInstanceError):
        session.access_token = "changed"  # type: ignore[misc]