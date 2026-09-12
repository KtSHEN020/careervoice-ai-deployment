from __future__ import annotations

import pytest

from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)

from backend.app.config import BackendSettings
from backend.app.usage_runtime import (
    build_daily_usage_status_provider,
)
from backend.app.usage_service import (
    DailyUsageService,
)


def database_environment() -> dict[str, str]:
    return {
        "DATABASE_HOST": (
            "example.pooler.supabase.com"
        ),
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "postgres",
        "DATABASE_USER": "runtime-user",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_SSLMODE": "require",
    }


def test_usage_runtime_is_unconfigured_without_database() -> None:
    provider = build_daily_usage_status_provider(
        settings=BackendSettings(
            environment="test",
        ),
        environment={},
    )

    assert provider is None


def test_usage_runtime_builds_persistent_service() -> None:
    provider = build_daily_usage_status_provider(
        settings=BackendSettings(
            environment="test",
            daily_ai_unit_limit=60,
        ),
        environment=database_environment(),
    )

    assert isinstance(
        provider,
        DailyUsageService,
    )

    assert isinstance(
        provider.repository,
        PostgresPersistentUsageRepository,
    )

    assert provider.daily_ai_unit_limit == 60


def test_usage_runtime_rejects_incomplete_database_configuration() -> None:
    environment = database_environment()

    environment.pop(
        "DATABASE_PASSWORD"
    )

    with pytest.raises(
        ValueError,
        match="Database configuration is incomplete",
    ):
        build_daily_usage_status_provider(
            settings=BackendSettings(
                environment="test",
            ),
            environment=environment,
        )