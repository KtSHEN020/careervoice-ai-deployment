"""Runtime construction for CareerVoice authentication."""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass

from careervoice_ai_web_app.login_controller import LoginController
from careervoice_ai_web_app.postgres_connection import (
    PostgresConnectionSettings,
    build_postgres_connection_factory,
)
from careervoice_ai_web_app.postgres_user_repository import (
    PostgresAppUserRepository,
)
from careervoice_ai_web_app.supabase_authentication import (
    SupabaseAuthenticationService,
)
from careervoice_ai_web_app.user_access import UserAccessService


@dataclass(frozen=True)
class SupabaseAuthenticationSettings:
    """Public Supabase settings required for email authentication."""

    url: str
    publishable_key: str

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> SupabaseAuthenticationSettings | None:
        """Load Supabase authentication settings from runtime configuration."""
        env = os.environ if environment is None else environment

        supplied = {
            "SUPABASE_URL": env.get(
                "SUPABASE_URL",
                "",
            ).strip(),
            "SUPABASE_PUBLISHABLE_KEY": env.get(
                "SUPABASE_PUBLISHABLE_KEY",
                "",
            ).strip(),
        }

        if not any(supplied.values()):
            return None

        missing = [
            key
            for key, value in supplied.items()
            if not value
        ]

        if missing:
            raise ValueError(
                "Supabase authentication configuration is incomplete. "
                "Missing: "
                + ", ".join(missing)
            )

        return cls(
            url=supplied["SUPABASE_URL"],
            publishable_key=supplied[
                "SUPABASE_PUBLISHABLE_KEY"
            ],
        )


def build_login_controller(
    *,
    state: MutableMapping[str, object],
    environment: Mapping[str, str] | None = None,
) -> LoginController:
    """Build the production login controller for CareerVoice AI."""
    supabase_settings = (
        SupabaseAuthenticationSettings.from_environment(
            environment
        )
    )

    if supabase_settings is None:
        raise RuntimeError(
            "Supabase authentication is not configured."
        )

    database_settings = (
        PostgresConnectionSettings.from_environment(
            environment
        )
    )

    if database_settings is None:
        raise RuntimeError(
            "CareerVoice user database is not configured."
        )

    authentication_service = (
        SupabaseAuthenticationService.from_credentials(
            url=supabase_settings.url,
            publishable_key=(
                supabase_settings.publishable_key
            ),
        )
    )

    user_repository = PostgresAppUserRepository(
        build_postgres_connection_factory(
            database_settings
        )
    )

    user_access_service = UserAccessService(
        user_repository
    )

    return LoginController(
        authentication_service=authentication_service,
        user_access_service=user_access_service,
        state=state,
    )