from uuid import uuid4

import pytest

from careervoice_ai_web_app.authentication import (
    AuthenticationError,
    AuthenticationSession,
)
from careervoice_ai_web_app.login_controller import (
    LoginController,
)
from careervoice_ai_web_app.ui_state import (
    AUTHENTICATED_APP_USER_KEY,
    AUTHENTICATION_SESSION_KEY,
)
from careervoice_ai_web_app.user_access import (
    UserDisabledError,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)


def _identity() -> AuthenticatedIdentity:
    return AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )


def _session() -> AuthenticationSession:
    return AuthenticationSession(
        identity=_identity(),
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=1_800_000_000,
    )


def _user(
    *,
    enabled: bool = True,
) -> AppUser:
    return AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=enabled,
    )


class FakeAuthenticationService:
    def __init__(self) -> None:
        self.requested_email: str | None = None
        self.verified_email: str | None = None
        self.verified_code: str | None = None
        self.session = _session()
        self.signed_out_sessions: list[
            AuthenticationSession
        ] = []
        self.sign_out_error: Exception | None = None

    def request_login_code(
        self,
        email: str,
    ) -> None:
        self.requested_email = email

    def verify_login_code(
        self,
        *,
        email: str,
        code: str,
    ) -> AuthenticationSession:
        self.verified_email = email
        self.verified_code = code
        return self.session

    def refresh_session(
        self,
        session: AuthenticationSession,
    ) -> AuthenticationSession:
        return session

    def sign_out(
        self,
        session: AuthenticationSession,
    ) -> None:
        self.signed_out_sessions.append(
            session
        )

        if self.sign_out_error is not None:
            raise self.sign_out_error


class FakeUserAccessService:
    def __init__(
        self,
        *,
        user: AppUser | None = None,
        error: Exception | None = None,
    ) -> None:
        self.user = user or _user()
        self.error = error
        self.identity_seen: AuthenticatedIdentity | None = None

    def authorize(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser:
        self.identity_seen = identity

        if self.error is not None:
            raise self.error

        return self.user


def _controller(
    *,
    authentication_service: FakeAuthenticationService | None = None,
    user_access_service: FakeUserAccessService | None = None,
    state: dict[str, object] | None = None,
) -> tuple[
    LoginController,
    FakeAuthenticationService,
    FakeUserAccessService,
    dict[str, object],
]:
    authentication = (
        authentication_service
        or FakeAuthenticationService()
    )

    access = (
        user_access_service
        or FakeUserAccessService()
    )

    session_state = (
        state
        if state is not None
        else {}
    )

    controller = LoginController(
        authentication_service=authentication,
        user_access_service=access,  # type: ignore[arg-type]
        state=session_state,
    )

    return (
        controller,
        authentication,
        access,
        session_state,
    )


def test_request_login_code_delegates_to_authentication_service() -> None:
    controller, authentication, _, _ = _controller()

    controller.request_login_code(
        "tester@example.com"
    )

    assert authentication.requested_email == (
        "tester@example.com"
    )


def test_verify_login_code_authenticates_and_authorizes() -> None:
    controller, authentication, access, state = (
        _controller()
    )

    user = controller.verify_login_code(
        email="tester@example.com",
        code="12345678",
    )

    assert authentication.verified_email == (
        "tester@example.com"
    )
    assert authentication.verified_code == "12345678"

    assert access.identity_seen == (
        authentication.session.identity
    )

    assert state[
        AUTHENTICATION_SESSION_KEY
    ] is authentication.session

    assert state[
        AUTHENTICATED_APP_USER_KEY
    ] is user

    assert controller.is_authenticated is True
    assert controller.current_user is user


def test_failed_authorization_does_not_store_login_state() -> None:
    authentication = FakeAuthenticationService()

    access = FakeUserAccessService(
        error=UserDisabledError(
            "Account disabled."
        )
    )

    controller, _, _, state = _controller(
        authentication_service=authentication,
        user_access_service=access,
    )

    with pytest.raises(
        UserDisabledError,
        match="disabled",
    ):
        controller.verify_login_code(
            email="tester@example.com",
            code="12345678",
        )

    assert AUTHENTICATION_SESSION_KEY not in state
    assert AUTHENTICATED_APP_USER_KEY not in state

    assert authentication.signed_out_sessions == [
        authentication.session
    ]


def test_failed_authorization_preserves_original_error_when_sign_out_fails() -> None:
    authentication = FakeAuthenticationService()
    authentication.sign_out_error = AuthenticationError(
        "Provider sign-out failed."
    )

    access = FakeUserAccessService(
        error=UserDisabledError(
            "Account disabled."
        )
    )

    controller, _, _, state = _controller(
        authentication_service=authentication,
        user_access_service=access,
    )

    with pytest.raises(
        UserDisabledError,
        match="disabled",
    ):
        controller.verify_login_code(
            email="tester@example.com",
            code="12345678",
        )

    assert state == {}


def test_sign_out_clears_entire_user_session_state() -> None:
    authentication = FakeAuthenticationService()
    session = authentication.session
    user = _user()

    state: dict[str, object] = {
        AUTHENTICATION_SESSION_KEY: session,
        AUTHENTICATED_APP_USER_KEY: user,
        "workspace_session_id": "workspace-123",
        "career_profile": {
            "target_roles": ["Software Engineer"],
        },
        "collected_jobs": [
            {
                "title": "Software Engineer",
            }
        ],
        "recommendations": {
            "results": [],
        },
        "voice_transcript_text": "private transcript",
        "ai_usage_units": 12,
        "profile_skills_4": "Python",
        "job_search_location_4": "Adelaide",
        "recommendation_max_results_2": 5,
    }

    controller, _, _, _ = _controller(
        authentication_service=authentication,
        state=state,
    )

    controller.sign_out()

    assert authentication.signed_out_sessions == [
        session
    ]

    assert state == {}
    assert controller.is_authenticated is False


def test_sign_out_clears_all_state_even_when_provider_fails() -> None:
    authentication = FakeAuthenticationService()
    authentication.sign_out_error = AuthenticationError(
        "Provider sign-out failed."
    )

    state: dict[str, object] = {
        AUTHENTICATION_SESSION_KEY: authentication.session,
        AUTHENTICATED_APP_USER_KEY: _user(),
        "career_profile": {
            "target_roles": ["Software Engineer"],
        },
        "voice_transcript_text": "private transcript",
        "collected_jobs": [
            {
                "title": "Software Engineer",
            }
        ],
        "ai_usage_units": 7,
        "profile_skills_3": "Python",
    }

    controller, _, _, _ = _controller(
        authentication_service=authentication,
        state=state,
    )

    with pytest.raises(
        AuthenticationError,
        match="Provider sign-out failed",
    ):
        controller.sign_out()

    assert state == {}


def test_invalid_session_state_values_are_not_trusted() -> None:
    state: dict[str, object] = {
        AUTHENTICATION_SESSION_KEY: "fake-session",
        AUTHENTICATED_APP_USER_KEY: "fake-user",
    }

    controller, _, _, _ = _controller(
        state=state
    )

    assert controller.current_session is None
    assert controller.current_user is None
    assert controller.is_authenticated is False


def test_sign_out_without_provider_session_clears_stale_user_state() -> None:
    state: dict[str, object] = {
        "career_profile": {
            "target_roles": ["Software Engineer"],
        },
        "collected_jobs": [],
        "voice_transcript_text": "private transcript",
        "profile_skills_2": "Python",
    }

    controller, authentication, _, _ = _controller(
        state=state
    )

    controller.sign_out()

    assert authentication.signed_out_sessions == []
    assert state == {}