from uuid import uuid4

import pytest

from careervoice_ai_web_app.ai_usage import (
    SessionAIUsageBudget,
)
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.usage_budget_factory import (
    build_ai_usage_budget,
)
from careervoice_ai_web_app.user_models import AppUser


def _user() -> AppUser:
    return AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )


def _database_environment() -> dict[str, str]:
    return {
        "DATABASE_HOST": "example.pooler.supabase.com",
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "postgres",
        "DATABASE_USER": "postgres.example",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_SSLMODE": "require",
    }


def test_unauthenticated_session_uses_session_budget() -> None:
    state: dict[str, object] = {}

    budget = build_ai_usage_budget(
        state=state,
        app_user=None,
        environment={},
    )

    assert isinstance(
        budget,
        SessionAIUsageBudget,
    )


def test_authenticated_user_uses_persistent_budget() -> None:
    user = _user()

    budget = build_ai_usage_budget(
        state={},
        app_user=user,
        environment=_database_environment(),
    )

    assert isinstance(
        budget,
        PersistentAIUsageBudget,
    )
    assert budget.user is user


def test_authenticated_user_requires_database_configuration() -> None:
    with pytest.raises(
        RuntimeError,
        match="database is not configured",
    ):
        build_ai_usage_budget(
            state={},
            app_user=_user(),
            environment={},
        )


def test_authenticated_user_rejects_partial_database_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="configuration is incomplete",
    ):
        build_ai_usage_budget(
            state={},
            app_user=_user(),
            environment={
                "DATABASE_HOST": "example.pooler.supabase.com",
            },
        )


def test_authenticated_user_rejects_invalid_database_port() -> None:
    environment = _database_environment()
    environment["DATABASE_PORT"] = "not-a-port"

    with pytest.raises(
        ValueError,
        match="DATABASE_PORT must be an integer",
    ):
        build_ai_usage_budget(
            state={},
            app_user=_user(),
            environment=environment,
        )