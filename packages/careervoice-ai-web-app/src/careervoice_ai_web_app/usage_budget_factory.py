"""Construct the appropriate AI usage safeguard for a web session."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from careervoice_ai_web_app.ai_usage import (
    SessionAIUsageBudget,
    SupportsAIUsageBudget,
)
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.postgres_connection import (
    PostgresConnectionSettings,
    build_postgres_connection_factory,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)
from careervoice_ai_web_app.user_models import AppUser


def build_ai_usage_budget(
    *,
    state: MutableMapping[str, object],
    app_user: AppUser | None,
    environment: Mapping[str, str] | None = None,
) -> SupportsAIUsageBudget:
    """Choose session or persistent usage according to authentication state."""
    if app_user is None:
        return SessionAIUsageBudget(state)

    settings = PostgresConnectionSettings.from_environment(
        environment
    )

    if settings is None:
        raise RuntimeError(
            "Persistent usage database is not configured."
        )

    repository = PostgresPersistentUsageRepository(
        build_postgres_connection_factory(settings)
    )

    return PersistentAIUsageBudget(
        repository=repository,
        user=app_user,
    )