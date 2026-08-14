from uuid import uuid4

import pytest

from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
    normalize_email,
)


def test_normalize_email_cleans_email_address() -> None:
    assert normalize_email("  Tester@Example.COM ") == "tester@example.com"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "missing-at-sign",
        "@example.com",
        "tester@",
        "tester@@example.com",
    ],
)
def test_normalize_email_rejects_invalid_email(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="valid email address|cannot be empty",
    ):
        normalize_email(value)


def test_authenticated_identity_normalizes_provider_values() -> None:
    identity = AuthenticatedIdentity(
        provider=" Supabase ",
        subject=" auth-user-123 ",
        email=" Tester@Example.com ",
    )

    assert identity.provider == "supabase"
    assert identity.subject == "auth-user-123"
    assert identity.email == "tester@example.com"


def test_app_user_has_careervoice_id_separate_from_auth_subject() -> None:
    user_id = uuid4()

    user = AppUser(
        id=user_id,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="supabase-user-456",
    )

    assert user.id == user_id
    assert str(user.id) != user.auth_subject


def test_app_user_matches_authenticated_identity() -> None:
    user = AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
    )

    identity = AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )

    assert user.matches_identity(identity) is True


def test_app_user_does_not_match_different_auth_subject() -> None:
    user = AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
    )

    identity = AuthenticatedIdentity(
        provider="supabase",
        subject="another-user",
        email="tester@example.com",
    )

    assert user.matches_identity(identity) is False


def test_app_user_can_be_disabled() -> None:
    user = AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=False,
    )

    assert user.enabled is False


def test_app_user_rejects_non_uuid_id() -> None:
    with pytest.raises(
        ValueError,
        match="must be a UUID",
    ):
        AppUser(
            id="user-123",  # type: ignore[arg-type]
            email="tester@example.com",
            auth_provider="supabase",
            auth_subject="auth-user-123",
        )