"""Provider-independent CareerVoice user repository contracts."""

from __future__ import annotations

from typing import Protocol

from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)


class AppUserRepository(Protocol):
    """Persistence operations required for CareerVoice users."""

    def find_by_identity(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser | None:
        """Find the CareerVoice user mapped to an authenticated identity."""
        ...

    def add(self, user: AppUser) -> None:
        """Persist a new CareerVoice user."""
        ...

    def set_enabled(
        self,
        user: AppUser,
        *,
        enabled: bool,
    ) -> None:
        """Enable or disable an existing CareerVoice user."""
        ...