import pytest

from preference_aware_job_recommender import config


def test_get_openai_api_key_returns_environment_value(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    api_key = config.get_openai_api_key()

    assert api_key == "test-api-key"


def test_get_openai_api_key_raises_error_when_missing(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        config.get_openai_api_key()


def test_create_openai_client_uses_validated_api_key(monkeypatch):
    created_client_values = {}

    class FakeOpenAI:
        def __init__(self, *, api_key: str) -> None:
            created_client_values["api_key"] = api_key

    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setattr(config, "OpenAI", FakeOpenAI)

    client = config.create_openai_client()

    assert isinstance(client, FakeOpenAI)
    assert created_client_values["api_key"] == "test-api-key"