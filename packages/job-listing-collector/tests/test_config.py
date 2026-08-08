import pytest

from job_listing_collector import config


def test_load_adzuna_config_returns_environment_values(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    monkeypatch.setenv("ADZUNA_COUNTRY", "AU")

    adzuna_config = config.load_adzuna_config()

    assert adzuna_config.app_id == "test-app-id"
    assert adzuna_config.app_key == "test-app-key"
    assert adzuna_config.country == "au"


def test_load_adzuna_config_defaults_country_to_au(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    monkeypatch.delenv("ADZUNA_COUNTRY", raising=False)

    adzuna_config = config.load_adzuna_config()

    assert adzuna_config.country == "au"


def test_load_adzuna_config_uses_default_country_when_blank(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    monkeypatch.setenv("ADZUNA_COUNTRY", "   ")

    adzuna_config = config.load_adzuna_config()

    assert adzuna_config.country == "au"


def test_load_adzuna_config_strips_environment_values(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "  test-app-id  ")
    monkeypatch.setenv("ADZUNA_APP_KEY", "  test-app-key  ")
    monkeypatch.setenv("ADZUNA_COUNTRY", "  AU  ")

    adzuna_config = config.load_adzuna_config()

    assert adzuna_config.app_id == "test-app-id"
    assert adzuna_config.app_key == "test-app-key"
    assert adzuna_config.country == "au"


def test_load_adzuna_config_raises_error_when_app_id_missing(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")

    with pytest.raises(RuntimeError, match="ADZUNA_APP_ID is not set"):
        config.load_adzuna_config()


def test_load_adzuna_config_raises_error_when_app_key_missing(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ADZUNA_APP_KEY is not set"):
        config.load_adzuna_config()


def test_create_adzuna_source_uses_validated_config(monkeypatch) -> None:
    created_source_values = {}

    class FakeAdzunaSource:
        def __init__(self, *, app_id: str, app_key: str, country: str) -> None:
            created_source_values["app_id"] = app_id
            created_source_values["app_key"] = app_key
            created_source_values["country"] = country

    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    monkeypatch.setenv("ADZUNA_COUNTRY", "AU")
    monkeypatch.setattr(config, "AdzunaSource", FakeAdzunaSource)

    source = config.create_adzuna_source()

    assert isinstance(source, FakeAdzunaSource)
    assert created_source_values["app_id"] == "test-app-id"
    assert created_source_values["app_key"] == "test-app-key"
    assert created_source_values["country"] == "au"