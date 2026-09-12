import pytest

from backend.app.config import (
    DEFAULT_DAILY_AI_UNIT_LIMIT,
    BackendSettings,
)


def test_backend_settings_use_safe_defaults() -> None:
    settings = BackendSettings.from_environment({})

    assert settings.environment == "development"
    assert settings.api_title == "CareerVoice AI API"
    assert settings.api_version == "0.1.0"
    assert (
        settings.daily_ai_unit_limit
        == DEFAULT_DAILY_AI_UNIT_LIMIT
    )


def test_backend_settings_read_environment_values() -> None:
    settings = BackendSettings.from_environment(
        {
            "CAREERVOICE_ENVIRONMENT": "production",
            "CAREERVOICE_DAILY_AI_UNIT_LIMIT": "25",
        }
    )

    assert settings.environment == "production"
    assert settings.daily_ai_unit_limit == 25


def test_backend_settings_reject_unknown_environment() -> None:
    with pytest.raises(
        ValueError,
        match="CAREERVOICE_ENVIRONMENT",
    ):
        BackendSettings.from_environment(
            {
                "CAREERVOICE_ENVIRONMENT": "staging",
            }
        )


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "-1",
        "not-a-number",
    ],
)
def test_backend_settings_reject_invalid_daily_limit(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="CAREERVOICE_DAILY_AI_UNIT_LIMIT",
    ):
        BackendSettings.from_environment(
            {
                "CAREERVOICE_DAILY_AI_UNIT_LIMIT": value,
            }
        )