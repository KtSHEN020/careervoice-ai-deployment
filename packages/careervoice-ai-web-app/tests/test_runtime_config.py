from __future__ import annotations

from careervoice_ai_web_app.runtime_config import get_capability_status


def test_no_external_capabilities_without_configuration() -> None:
    status = get_capability_status({})

    assert status.openai_available is False
    assert status.adzuna_available is False
    assert status.ai_features_available is False
    assert status.job_collection_available is False


def test_openai_available_when_api_key_is_configured() -> None:
    status = get_capability_status(
        {
            "OPENAI_API_KEY": "test-openai-key",
        }
    )

    assert status.openai_available is True
    assert status.ai_features_available is True
    assert status.adzuna_available is False


def test_adzuna_requires_both_credentials() -> None:
    status = get_capability_status(
        {
            "ADZUNA_APP_ID": "test-app-id",
        }
    )

    assert status.adzuna_available is False


def test_adzuna_available_when_both_credentials_are_configured() -> None:
    status = get_capability_status(
        {
            "ADZUNA_APP_ID": "test-app-id",
            "ADZUNA_APP_KEY": "test-app-key",
        }
    )

    assert status.adzuna_available is True
    assert status.job_collection_available is True


def test_blank_configuration_values_are_not_available() -> None:
    status = get_capability_status(
        {
            "OPENAI_API_KEY": "   ",
            "ADZUNA_APP_ID": "",
            "ADZUNA_APP_KEY": "   ",
        }
    )

    assert status.openai_available is False
    assert status.adzuna_available is False