"""Runtime authentication construction for the CareerVoice AI API."""

from __future__ import annotations

from collections.abc import Mapping

from careervoice_ai_web_app.auth_runtime import (
    SupabaseAuthenticationSettings,
)
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
from careervoice_ai_web_app.user_access import (
    UserAccessService,
)

from backend.app.security import (
    CareerVoiceCurrentUserResolver,
    CurrentUserResolver,
    UnconfiguredCurrentUserResolver,
)


def build_current_user_resolver(
    environment: Mapping[str, str] | None = None,
) -> CurrentUserResolver:
    """Build authentication and authorization for protected API routes."""
    supabase_settings = (
        SupabaseAuthenticationSettings.from_environment(
            environment
        )
    )

    database_settings = (
        PostgresConnectionSettings.from_environment(
            environment
        )
    )

    if (
        supabase_settings is None
        and database_settings is None
    ):
        return UnconfiguredCurrentUserResolver()

    if supabase_settings is None:
        raise RuntimeError(
            "Supabase authentication is not configured."
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

    return CareerVoiceCurrentUserResolver(
        authentication_service=authentication_service,
        user_access_service=user_access_service,
    )