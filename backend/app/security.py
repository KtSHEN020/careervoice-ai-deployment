"""Authentication boundaries for the CareerVoice AI API."""

from __future__ import annotations

from typing import Annotated, Protocol

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from careervoice_ai_web_app.authentication import (
    AccessTokenAuthenticationService,
    AuthenticationError,
)
from careervoice_ai_web_app.user_access import (
    UserAccessError,
    UserAccessService,
)
from careervoice_ai_web_app.user_models import AppUser


class InvalidAccessTokenError(RuntimeError):
    """Raised when an API access token cannot be authenticated."""


class CurrentUserAccessDeniedError(RuntimeError):
    """Raised when an authenticated identity cannot use CareerVoice."""


class CurrentUserResolverUnavailableError(RuntimeError):
    """Raised when production user resolution is not configured."""


class CurrentUserResolver(Protocol):
    """Resolve an API access token into an authorized CareerVoice user."""

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        """Authenticate an access token and return its CareerVoice user."""
        ...


class CareerVoiceCurrentUserResolver:
    """Authenticate bearer tokens and authorize CareerVoice users."""

    def __init__(
        self,
        authentication_service: AccessTokenAuthenticationService,
        user_access_service: UserAccessService,
    ) -> None:
        self._authentication_service = authentication_service
        self._user_access_service = user_access_service

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        """Resolve an access token into an authorized CareerVoice user."""
        try:
            identity = (
                self._authentication_service.authenticate_access_token(
                    access_token
                )
            )
        except AuthenticationError as exc:
            raise InvalidAccessTokenError(
                "Access token could not be authenticated."
            ) from exc

        try:
            return self._user_access_service.authorize(
                identity
            )
        except UserAccessError as exc:
            raise CurrentUserAccessDeniedError(
                "Authenticated user is not authorized for CareerVoice."
            ) from exc


class UnconfiguredCurrentUserResolver:
    """Reject protected requests until production auth is configured."""

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        del access_token

        raise CurrentUserResolverUnavailableError(
            "API authentication is not configured."
        )


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def _unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AppUser:
    """Return the authenticated CareerVoice user for this request."""
    if (
        credentials is None
        or credentials.scheme.casefold() != "bearer"
        or not credentials.credentials.strip()
    ):
        raise _unauthorized_exception()

    resolver: CurrentUserResolver = (
        request.app.state.current_user_resolver
    )

    try:
        return resolver.resolve(
            credentials.credentials.strip()
        )
    except InvalidAccessTokenError as exc:
        raise _unauthorized_exception() from exc
    except CurrentUserAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CareerVoice access is not permitted.",
        ) from exc
    except CurrentUserResolverUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable.",
        ) from exc