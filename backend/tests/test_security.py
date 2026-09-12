from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import pytest

from careervoice_ai_web_app.authentication import (
    AuthenticationError,
)
from careervoice_ai_web_app.user_access import (
    UserDisabledError,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)

from backend.app.security import (
    CareerVoiceCurrentUserResolver,
    CurrentUserAccessDeniedError,
    InvalidAccessTokenError,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


@dataclass
class FakeAccessTokenAuthenticationService:
    identity: AuthenticatedIdentity
    should_fail: bool = False

    token_seen: str | None = None

    def authenticate_access_token(
        self,
        access_token: str,
    ) -> AuthenticatedIdentity:
        self.token_seen = access_token

        if self.should_fail:
            raise AuthenticationError(
                "Access token is invalid."
            )

        return self.identity


@dataclass
class FakeUserAccessService:
    user: AppUser
    should_fail: bool = False

    identity_seen: AuthenticatedIdentity | None = None

    def authorize(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser:
        self.identity_seen = identity

        if self.should_fail:
            raise UserDisabledError(
                "This CareerVoice account is currently disabled."
            )

        return self.user


def create_identity() -> AuthenticatedIdentity:
    return AuthenticatedIdentity(
        provider="supabase",
        subject="provider-user-123",
        email="tester@example.com",
    )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_resolver_authenticates_and_authorizes_user() -> None:
    identity = create_identity()
    user = create_user()

    authentication_service = (
        FakeAccessTokenAuthenticationService(
            identity=identity
        )
    )
    user_access_service = FakeUserAccessService(
        user=user
    )

    resolver = CareerVoiceCurrentUserResolver(
        authentication_service=authentication_service,
        user_access_service=user_access_service,
    )

    resolved_user = resolver.resolve(
        "test-access-token"
    )

    assert resolved_user is user
    assert (
        authentication_service.token_seen
        == "test-access-token"
    )
    assert user_access_service.identity_seen is identity


def test_resolver_translates_authentication_failure() -> None:
    authentication_service = (
        FakeAccessTokenAuthenticationService(
            identity=create_identity(),
            should_fail=True,
        )
    )
    user_access_service = FakeUserAccessService(
        user=create_user()
    )

    resolver = CareerVoiceCurrentUserResolver(
        authentication_service=authentication_service,
        user_access_service=user_access_service,
    )

    with pytest.raises(
        InvalidAccessTokenError,
        match="could not be authenticated",
    ):
        resolver.resolve(
            "invalid-access-token"
        )

    assert user_access_service.identity_seen is None


def test_resolver_translates_user_access_failure() -> None:
    authentication_service = (
        FakeAccessTokenAuthenticationService(
            identity=create_identity()
        )
    )
    user_access_service = FakeUserAccessService(
        user=create_user(),
        should_fail=True,
    )

    resolver = CareerVoiceCurrentUserResolver(
        authentication_service=authentication_service,
        user_access_service=user_access_service,
    )

    with pytest.raises(
        CurrentUserAccessDeniedError,
        match="not authorized",
    ):
        resolver.resolve(
            "valid-access-token"
        )