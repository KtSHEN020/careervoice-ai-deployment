"""Authentication session coordination for CareerVoice AI."""

from __future__ import annotations

from collections.abc import MutableMapping

from careervoice_ai_web_app.authentication import (
    AuthenticationError,
    AuthenticationService,
    AuthenticationSession,
)
from careervoice_ai_web_app.ui_state import (
    AUTHENTICATED_APP_USER_KEY,
    AUTHENTICATION_SESSION_KEY,
    clear_user_session_state,
)
from careervoice_ai_web_app.user_access import (
    UserAccessError,
    UserAccessService,
)
from careervoice_ai_web_app.user_models import AppUser


class LoginController:
    """Coordinate authentication and CareerVoice authorization."""

    def __init__(
        self,
        *,
        authentication_service: AuthenticationService,
        user_access_service: UserAccessService,
        state: MutableMapping[str, object],
    ) -> None:
        self._authentication_service = authentication_service
        self._user_access_service = user_access_service
        self._state = state

    @property
    def current_session(self) -> AuthenticationSession | None:
        """Return the authenticated provider session, when available."""
        value = self._state.get(
            AUTHENTICATION_SESSION_KEY
        )

        if isinstance(value, AuthenticationSession):
            return value

        return None

    @property
    def current_user(self) -> AppUser | None:
        """Return the authorized CareerVoice user, when available."""
        value = self._state.get(
            AUTHENTICATED_APP_USER_KEY
        )

        if isinstance(value, AppUser):
            return value

        return None

    @property
    def is_authenticated(self) -> bool:
        """Return whether the session has an authorized CareerVoice user."""
        return (
            self.current_session is not None
            and self.current_user is not None
        )

    def request_login_code(
        self,
        email: str,
    ) -> None:
        """Request an email login code."""
        self._authentication_service.request_login_code(
            email
        )

    def verify_login_code(
        self,
        *,
        email: str,
        code: str,
    ) -> AppUser:
        """Authenticate and authorize a CareerVoice user."""
        session = (
            self._authentication_service.verify_login_code(
                email=email,
                code=code,
            )
        )

        try:
            user = self._user_access_service.authorize(
                session.identity
            )
        except UserAccessError:
            self._best_effort_provider_sign_out(
                session
            )
            raise

        self._state[
            AUTHENTICATION_SESSION_KEY
        ] = session

        self._state[
            AUTHENTICATED_APP_USER_KEY
        ] = user

        return user

    def sign_out(self) -> None:
        """End the provider session and clear all local user state."""
        session = self.current_session

        try:
            if session is not None:
                self._authentication_service.sign_out(
                    session
                )
        finally:
            clear_user_session_state(
                self._state
            )

    def _best_effort_provider_sign_out(
        self,
        session: AuthenticationSession,
    ) -> None:
        """Close a provider session after CareerVoice authorization fails."""
        try:
            self._authentication_service.sign_out(
                session
            )
        except AuthenticationError:
            pass