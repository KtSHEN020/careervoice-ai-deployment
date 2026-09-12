from __future__ import annotations

import pytest

from backend.app.auth_runtime import (
    build_current_user_resolver,
)
from backend.app.security import (
    CareerVoiceCurrentUserResolver,
    UnconfiguredCurrentUserResolver,
)


def complete_environment() -> dict[str, str]:
    return {
        "SUPABASE_URL": (
            "https://example.supabase.co"
        ),
        "SUPABASE_PUBLISHABLE_KEY": (
            "test-publishable-key"
        ),
        "DATABASE_HOST": (
            "example.pooler.supabase.com"
        ),
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "postgres",
        "DATABASE_USER": "runtime-user",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_SSLMODE": "require",
    }


def test_runtime_uses_unconfigured_resolver_without_auth_settings() -> None:
    resolver = build_current_user_resolver(
        {}
    )

    assert isinstance(
        resolver,
        UnconfiguredCurrentUserResolver,
    )


def test_runtime_requires_database_when_supabase_is_configured() -> None:
    with pytest.raises(
        RuntimeError,
        match="user database is not configured",
    ):
        build_current_user_resolver(
            {
                "SUPABASE_URL": (
                    "https://example.supabase.co"
                ),
                "SUPABASE_PUBLISHABLE_KEY": (
                    "test-publishable-key"
                ),
            }
        )


def test_runtime_requires_supabase_when_database_is_configured() -> None:
    environment = complete_environment()

    environment.pop(
        "SUPABASE_URL"
    )
    environment.pop(
        "SUPABASE_PUBLISHABLE_KEY"
    )

    with pytest.raises(
        RuntimeError,
        match="Supabase authentication is not configured",
    ):
        build_current_user_resolver(
            environment
        )


def test_runtime_builds_real_current_user_resolver() -> None:
    resolver = build_current_user_resolver(
        complete_environment()
    )

    assert isinstance(
        resolver,
        CareerVoiceCurrentUserResolver,
    )