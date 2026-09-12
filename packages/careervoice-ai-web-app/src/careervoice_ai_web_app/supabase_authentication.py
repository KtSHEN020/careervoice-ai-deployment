"""Supabase implementation of CareerVoice authentication."""

from __future__ import annotations

from typing import Protocol

from supabase import create_client
from supabase.client import ClientOptions

from careervoice_ai_web_app.authentication import (
    AuthenticationError,
    AuthenticationSession,
    AuthenticationSessionExpiredError,
    InvalidLoginCodeError,
)
from careervoice_ai_web_app.user_models import (
    AuthenticatedIdentity,
    normalize_email,
)


class _SupabaseAuthClient(Protocol):
    """Subset of the Supabase Auth client required by CareerVoice."""

    def sign_in_with_otp(
        self,
        credentials: dict[str, object],
    ) -> object:
        ...

    def verify_otp(
        self,
        params: dict[str, object],
    ) -> object:
        ...

    def get_user(
        self,
        jwt: str | None = None,
    ) -> object:
        ...

    def refresh_session(
        self,
        refresh_token: str | None = None,
    ) -> object:
        ...

    def set_session(
        self,
        access_token: str,
        refresh_token: str,
    ) -> object:
        ...

    def sign_out(
        self,
        options: dict[str, str] | None = None,
    ) -> object:
        ...


def _normalize_login_code(value: object) -> str:
    if not isinstance(value, str):
        raise InvalidLoginCodeError("Login code must be text.")

    code = value.strip()

    if not code:
        raise InvalidLoginCodeError("Login code cannot be empty.")

    return code


def _authenticated_identity_from_user(
    provider_user: object,
) -> AuthenticatedIdentity:
    provider_user_id = getattr(
        provider_user,
        "id",
        None,
    )
    provider_email = getattr(
        provider_user,
        "email",
        None,
    )

    if provider_user_id is None:
        raise AuthenticationError(
            "Authentication provider returned an invalid user identity."
        )

    try:
        normalized_provider_email = normalize_email(
            provider_email
        )
    except ValueError as exc:
        raise AuthenticationError(
            "Authentication provider returned an invalid user email."
        ) from exc

    return AuthenticatedIdentity(
        provider="supabase",
        subject=str(provider_user_id),
        email=normalized_provider_email,
    )


def _authentication_session_from_response(
    response: object,
    *,
    expected_email: str,
) -> AuthenticationSession:
    provider_session = getattr(response, "session", None)
    provider_user = getattr(response, "user", None)

    if provider_session is None or provider_user is None:
        raise AuthenticationError(
            "Authentication provider returned an incomplete session."
        )

    identity = _authenticated_identity_from_user(
        provider_user
    )

    if identity.email != expected_email:
        raise AuthenticationError(
            "Authenticated email does not match the requested account."
        )

    access_token = getattr(provider_session, "access_token", None)
    refresh_token = getattr(provider_session, "refresh_token", None)
    expires_at = getattr(provider_session, "expires_at", None)

    if not isinstance(access_token, str) or not access_token.strip():
        raise AuthenticationError(
            "Authentication provider returned an invalid access token."
        )

    return AuthenticationSession(
        identity=identity,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )


class SupabaseAuthenticationService:
    """Authenticate approved CareerVoice users through Supabase email OTP."""

    def __init__(
        self,
        auth_client: _SupabaseAuthClient,
    ) -> None:
        self._auth = auth_client

    @classmethod
    def from_credentials(
        cls,
        *,
        url: str,
        publishable_key: str,
    ) -> SupabaseAuthenticationService:
        """Create a service from Supabase project credentials."""
        normalized_url = url.strip()
        normalized_key = publishable_key.strip()

        if not normalized_url:
            raise ValueError("Supabase URL cannot be empty.")

        if not normalized_key:
            raise ValueError("Supabase publishable key cannot be empty.")

        client = create_client(
            normalized_url,
            normalized_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )

        return cls(client.auth)

    def authenticate_access_token(
        self,
        access_token: str,
    ) -> AuthenticatedIdentity:
        """Validate an access token and return its Supabase identity."""
        if not isinstance(access_token, str):
            raise AuthenticationError(
                "Access token must be text."
            )

        normalized_token = access_token.strip()

        if not normalized_token:
            raise AuthenticationError(
                "Access token cannot be empty."
            )

        try:
            response = self._auth.get_user(
                normalized_token
            )
        except Exception as exc:
            raise AuthenticationError(
                "Access token is invalid or expired."
            ) from exc

        provider_user = getattr(
            response,
            "user",
            None,
        )

        if provider_user is None:
            raise AuthenticationError(
                "Authentication provider returned an invalid user."
            )

        return _authenticated_identity_from_user(
            provider_user
        )

    def request_login_code(self, email: str) -> None:
        """Send an OTP only for an already existing Supabase account."""
        normalized_email = normalize_email(email)

        try:
            self._auth.sign_in_with_otp(
                {
                    "email": normalized_email,
                    "options": {
                        "should_create_user": False,
                    },
                }
            )
        except Exception as exc:
            # Keep the message deliberately generic so callers do not
            # reveal whether a particular email is an approved account.
            raise AuthenticationError(
                "Unable to request a login code."
            ) from exc

    def verify_login_code(
        self,
        *,
        email: str,
        code: str,
    ) -> AuthenticationSession:
        """Verify an email OTP and translate it into CareerVoice state."""
        normalized_email = normalize_email(email)
        normalized_code = _normalize_login_code(code)

        try:
            response = self._auth.verify_otp(
                {
                    "email": normalized_email,
                    "token": normalized_code,
                    "type": "email",
                }
            )
        except Exception as exc:
            raise InvalidLoginCodeError(
                "Login code is invalid or expired."
            ) from exc

        return _authentication_session_from_response(
            response,
            expected_email=normalized_email,
        )

    def refresh_session(
        self,
        session: AuthenticationSession,
    ) -> AuthenticationSession:
        """Refresh an existing Supabase authentication session."""
        if session.refresh_token is None:
            raise AuthenticationSessionExpiredError(
                "Authentication session cannot be refreshed."
            )

        try:
            response = self._auth.refresh_session(
                session.refresh_token
            )
        except Exception as exc:
            raise AuthenticationSessionExpiredError(
                "Authentication session has expired."
            ) from exc

        try:
            return _authentication_session_from_response(
                response,
                expected_email=session.identity.email,
            )
        except AuthenticationError as exc:
            raise AuthenticationSessionExpiredError(
                "Authentication session could not be refreshed."
            ) from exc

    def sign_out(
        self,
        session: AuthenticationSession,
    ) -> None:
        """Sign out only the current CareerVoice session."""
        if session.refresh_token is None:
            raise AuthenticationSessionExpiredError(
                "Authentication session cannot be signed out."
            )

        try:
            self._auth.set_session(
                session.access_token,
                session.refresh_token,
            )

            self._auth.sign_out(
                {
                    "scope": "local",
                }
            )
        except Exception as exc:
            raise AuthenticationError(
                "Unable to sign out."
            ) from exc