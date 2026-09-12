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