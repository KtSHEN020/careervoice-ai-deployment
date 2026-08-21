"""CareerVoice authorization rules for authenticated users."""

from __future__ import annotations

from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)
from careervoice_ai_web_app.user_repository import AppUserRepository


class UserAccessError(RuntimeError):
    """Base error raised when CareerVoice access cannot be granted."""


class UserNotRegisteredError(UserAccessError):
    """Raised when no CareerVoice account maps to an authenticated identity."""


class UserDisabledError(UserAccessError):
    """Raised when a CareerVoice account has been disabled."""


class UserIdentityMismatchError(UserAccessError):
    """Raised when authenticated identity data does not match the account."""


class UserAccessService:
    """Authorize authenticated identities for CareerVoice access."""

    def __init__(
        self,
        repository: AppUserRepository,
    ) -> None:
        self._repository = repository

    def authorize(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser:
        """Resolve and authorize an authenticated CareerVoice user."""
        user = self._repository.find_by_identity(identity)

        if user is None:
            raise UserNotRegisteredError(
                "This account is not registered for CareerVoice access."
            )

        if not user.enabled:
            raise UserDisabledError(
                "This CareerVoice account is currently disabled."
            )

        if user.email != identity.email:
            raise UserIdentityMismatchError(
                "Authenticated email does not match the CareerVoice account."
            )

        if not user.matches_identity(identity):
            raise UserIdentityMismatchError(
                "Authenticated identity does not match the CareerVoice account."
            )

        return user