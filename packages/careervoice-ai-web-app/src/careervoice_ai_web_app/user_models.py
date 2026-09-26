"""Provider-independent user identity models for CareerVoice AI."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


def normalize_email(value: object) -> str:
    """Normalize an email address used by a CareerVoice account."""
    if not isinstance(value, str):
        raise ValueError("User email must be text.")

    email = value.strip().casefold()

    if not email:
        raise ValueError("User email cannot be empty.")

    local_part, separator, domain = email.partition("@")

    if (
        separator != "@"
        or not local_part
        or not domain
        or "@" in domain
    ):
        raise ValueError("User email must be a valid email address.")

    return email


def normalize_auth_provider(value: object) -> str:
    """Normalize the name of an external authentication provider."""
    if not isinstance(value, str):
        raise ValueError("Authentication provider must be text.")

    provider = value.strip().casefold()

    if not provider:
        raise ValueError("Authentication provider cannot be empty.")

    return provider


def normalize_auth_subject(value: object) -> str:
    """Normalize the stable user identifier supplied by an auth provider."""
    if not isinstance(value, str):
        raise ValueError("Authentication subject must be text.")

    subject = value.strip()

    if not subject:
        raise ValueError("Authentication subject cannot be empty.")

    return subject


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """Identity returned by an external authentication provider."""

    provider: str
    subject: str
    email: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider",
            normalize_auth_provider(self.provider),
        )
        object.__setattr__(
            self,
            "subject",
            normalize_auth_subject(self.subject),
        )
        object.__setattr__(
            self,
            "email",
            normalize_email(self.email),
        )


@dataclass(frozen=True)
class AppUser:
    """CareerVoice user independent of the authentication provider."""

    id: UUID
    email: str
    auth_provider: str
    auth_subject: str
    enabled: bool = True
    ai_quota_exempt: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise ValueError("CareerVoice user ID must be a UUID.")

        object.__setattr__(
            self,
            "email",
            normalize_email(self.email),
        )
        object.__setattr__(
            self,
            "auth_provider",
            normalize_auth_provider(self.auth_provider),
        )
        object.__setattr__(
            self,
            "auth_subject",
            normalize_auth_subject(self.auth_subject),
        )

        if not isinstance(self.enabled, bool):
            raise ValueError("User enabled state must be boolean.")
        if not isinstance(
            self.ai_quota_exempt,
            bool,
        ):
            raise ValueError(
                "AI quota exemption state must be boolean."
            )

    def matches_identity(
        self,
        identity: AuthenticatedIdentity,
    ) -> bool:
        """Return whether an authenticated identity belongs to this user."""
        return (
            self.auth_provider == identity.provider
            and self.auth_subject == identity.subject
        )