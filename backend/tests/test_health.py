from fastapi.testclient import TestClient

from backend.app.config import BackendSettings
from backend.app.main import (
    create_app,
    create_runtime_app,
)


def test_health_check() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
        )
    )
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "careervoice-api",
    }


def test_application_metadata_comes_from_settings() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
            api_title="CareerVoice Test API",
            api_version="9.9.9",
        )
    )

    assert app.title == "CareerVoice Test API"
    assert app.version == "9.9.9"


def test_runtime_app_starts_without_auth_configuration() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )
    client = TestClient(app)

    response = client.get(
        "/health"
    )

    assert response.status_code == 200


def test_runtime_app_fails_closed_without_auth_configuration() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )
    client = TestClient(app)

    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer test-token",
        },
    )

    assert response.status_code == 503


def test_runtime_app_configures_usage_service_with_database() -> None:
    environment = {
        "CAREERVOICE_ENVIRONMENT": "test",
        "CAREERVOICE_DAILY_AI_UNIT_LIMIT": "60",
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

    app = create_runtime_app(
        environment
    )

    provider = (
        app.state.daily_usage_status_provider
    )

    assert provider is not None
    assert provider.daily_ai_unit_limit == 60


def test_cors_allows_configured_frontend_origin() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
            cors_origins=(
                "http://localhost:5173",
            ),
        )
    )

    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": (
                "http://localhost:5173"
            ),
            "Access-Control-Request-Method": (
                "GET"
            ),
        },
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "access-control-allow-origin"
        ]
        == "http://localhost:5173"
    )


def test_cors_does_not_allow_unknown_origin() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
            cors_origins=(
                "http://localhost:5173",
            ),
        )
    )

    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": (
                "https://unexpected.example.com"
            ),
            "Access-Control-Request-Method": (
                "GET"
            ),
        },
    )

    assert (
        "access-control-allow-origin"
        not in response.headers
    )