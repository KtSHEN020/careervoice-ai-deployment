from uuid import uuid4

import pytest

from careervoice_ai_web_app.user_access import (
    UserAccessService,
    UserDisabledError,
    UserIdentityMismatchError,
    UserNotRegisteredError,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)


class FakeUserRepository:
    def __init__(
        self,
        user: AppUser | None = None,
    ) -> None:
        self.user = user
        self.identity_seen: AuthenticatedIdentity | None = None

    def find_by_identity(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser | None:
        self.identity_seen = identity
        return self.user

    def add(self, user: AppUser) -> None:
        self.user = user

    def set_enabled(
        self,
        user: AppUser,
        *,
        enabled: bool,
    ) -> None:
        self.user = AppUser(
            id=user.id,
            email=user.email,
            auth_provider=user.auth_provider,
            auth_subject=user.auth_subject,
            enabled=enabled,
        )


def _identity(
    *,
    email: str = "tester@example.com",
    subject: str = "auth-user-123",
) -> AuthenticatedIdentity:
    return AuthenticatedIdentity(
        provider="supabase",
        subject=subject,
        email=email,
    )


def _user(
    *,
    email: str = "tester@example.com",
    subject: str = "auth-user-123",
    enabled: bool = True,
) -> AppUser:
    return AppUser(
        id=uuid4(),
        email=email,
        auth_provider="supabase",
        auth_subject=subject,
        enabled=enabled,
    )


def test_authorize_returns_enabled_matching_user() -> None:
    user = _user()
    repository = FakeUserRepository(user)
    service = UserAccessService(repository)

    identity = _identity()

    authorized = service.authorize(identity)

    assert authorized is user
    assert repository.identity_seen is identity


def test_authorize_rejects_missing_careervoice_user() -> None:
    service = UserAccessService(
        FakeUserRepository(None)
    )

    with pytest.raises(
        UserNotRegisteredError,
        match="not registered",
    ):
        service.authorize(_identity())


def test_authorize_rejects_disabled_user() -> None:
    service = UserAccessService(
        FakeUserRepository(
            _user(enabled=False)
        )
    )

    with pytest.raises(
        UserDisabledError,
        match="currently disabled",
    ):
        service.authorize(_identity())


def test_authorize_rejects_different_email() -> None:
    service = UserAccessService(
        FakeUserRepository(
            _user(email="approved@example.com")
        )
    )

    with pytest.raises(
        UserIdentityMismatchError,
        match="email does not match",
    ):
        service.authorize(
            _identity(email="different@example.com")
        )


def test_authorize_rejects_different_auth_subject() -> None:
    service = UserAccessService(
        FakeUserRepository(
            _user(subject="approved-auth-user")
        )
    )

    with pytest.raises(
        UserIdentityMismatchError,
        match="identity does not match",
    ):
        service.authorize(
            _identity(subject="different-auth-user")
        )