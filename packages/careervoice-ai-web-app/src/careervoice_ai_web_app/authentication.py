"""Provider-independent authentication contracts for CareerVoice AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from careervoice_ai_web_app.user_models import AuthenticatedIdentity


class AuthenticationError(RuntimeError):
    """Base error raised when authentication cannot be completed."""


class InvalidLoginCodeError(AuthenticationError):
    """Raised when a supplied login code cannot be verified."""


class AuthenticationSessionExpiredError(AuthenticationError):
    """Raised when an authentication session can no longer be refreshed."""


@dataclass(frozen=True)
class AuthenticationSession:
    """Provider-independent authenticated session state.

    Tokens are treated as opaque credentials. CareerVoice must not interpret
    their contents; only the authentication provider implementation should.
    """

    identity: AuthenticatedIdentity
    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.access_token, str):
            raise ValueError("Access token must be text.")

        access_token = self.access_token.strip()

        if not access_token:
            raise ValueError("Access token cannot be empty.")

        object.__setattr__(self, "access_token", access_token)

        if self.refresh_token is not None:
            if not isinstance(self.refresh_token, str):
                raise ValueError("Refresh token must be text.")

            refresh_token = self.refresh_token.strip()

            if not refresh_token:
                raise ValueError("Refresh token cannot be empty.")

            object.__setattr__(self, "refresh_token", refresh_token)

        if self.expires_at is not None:
            if (
                not isinstance(self.expires_at, int)
                or isinstance(self.expires_at, bool)
                or self.expires_at < 0
            ):
                raise ValueError(
                    "Session expiry must be a non-negative integer."
                )


class AuthenticationService(Protocol):
    """Authentication operations required by the CareerVoice application."""

    def request_login_code(self, email: str) -> None:
        """Request a one-time login code for an approved account."""
        ...

    def verify_login_code(
        self,
        *,
        email: str,
        code: str,
    ) -> AuthenticationSession:
        """Verify a login code and return an authenticated session."""
        ...

    def refresh_session(
        self,
        session: AuthenticationSession,
    ) -> AuthenticationSession:
        """Refresh an authenticated session when supported."""
        ...

    def sign_out(
        self,
        session: AuthenticationSession,
    ) -> None:
        """End an authenticated session."""
        ...