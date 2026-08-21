import pytest

from careervoice_ai_web_app.auth_runtime import (
    SupabaseAuthenticationSettings,
    build_login_controller,
)
from careervoice_ai_web_app.login_controller import (
    LoginController,
)


def _environment() -> dict[str, str]:
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
        "DATABASE_USER": "postgres.example",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_SSLMODE": "require",
    }


def test_supabase_settings_are_absent_without_configuration() -> None:
    settings = (
        SupabaseAuthenticationSettings.from_environment(
            {}
        )
    )

    assert settings is None


def test_supabase_settings_load_complete_configuration() -> None:
    settings = (
        SupabaseAuthenticationSettings.from_environment(
            {
                "SUPABASE_URL": (
                    "https://example.supabase.co"
                ),
                "SUPABASE_PUBLISHABLE_KEY": (
                    "test-publishable-key"
                ),
            }
        )
    )

    assert settings is not None
    assert settings.url == (
        "https://example.supabase.co"
    )
    assert settings.publishable_key == (
        "test-publishable-key"
    )


@pytest.mark.parametrize(
    "environment",
    [
        {
            "SUPABASE_URL": (
                "https://example.supabase.co"
            ),
        },
        {
            "SUPABASE_PUBLISHABLE_KEY": (
                "test-publishable-key"
            ),
        },
    ],
)
def test_supabase_settings_reject_partial_configuration(
    environment: dict[str, str],
) -> None:
    with pytest.raises(
        ValueError,
        match="configuration is incomplete",
    ):
        (
            SupabaseAuthenticationSettings
            .from_environment(
                environment
            )
        )


def test_login_controller_requires_supabase_configuration() -> None:
    environment = _environment()

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
        build_login_controller(
            state={},
            environment=environment,
        )


def test_login_controller_requires_database_configuration() -> None:
    environment = {
        "SUPABASE_URL": (
            "https://example.supabase.co"
        ),
        "SUPABASE_PUBLISHABLE_KEY": (
            "test-publishable-key"
        ),
    }

    with pytest.raises(
        RuntimeError,
        match="user database is not configured",
    ):
        build_login_controller(
            state={},
            environment=environment,
        )


def test_login_controller_builds_with_complete_configuration() -> None:
    state: dict[str, object] = {}

    controller = build_login_controller(
        state=state,
        environment=_environment(),
    )

    assert isinstance(
        controller,
        LoginController,
    )
    assert controller.current_user is None
    assert controller.current_session is None
    assert controller.is_authenticated is False