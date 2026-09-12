"""Runtime construction for CareerVoice daily usage services."""

from __future__ import annotations

from collections.abc import Mapping

from careervoice_ai_web_app.postgres_connection import (
    PostgresConnectionSettings,
    build_postgres_connection_factory,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)

from backend.app.config import BackendSettings
from backend.app.usage_service import (
    DailyUsageService,
    DailyUsageStatusProvider,
)


def build_daily_usage_status_provider(
    *,
    settings: BackendSettings,
    environment: Mapping[str, str] | None = None,
) -> DailyUsageStatusProvider | None:
    """Build persistent daily usage reporting for the API."""
    database_settings = (
        PostgresConnectionSettings.from_environment(
            environment
        )
    )

    if database_settings is None:
        return None

    repository = PostgresPersistentUsageRepository(
        build_postgres_connection_factory(
            database_settings
        )
    )

    return DailyUsageService(
        repository=repository,
        daily_ai_unit_limit=(
            settings.daily_ai_unit_limit
        ),
    )