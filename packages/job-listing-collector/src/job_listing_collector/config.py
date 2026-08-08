import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

from job_listing_collector.sources import AdzunaSource


class AdzunaConfig(BaseModel):
    """
    Validated configuration for the Adzuna source adapter.
    """

    model_config = ConfigDict(extra="forbid")

    app_id: str = Field(min_length=1)
    app_key: str = Field(min_length=1)
    country: str = Field(default="au", min_length=2)

    @field_validator("app_id", "app_key", "country", mode="before")
    @classmethod
    def strip_string_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.lower()


def load_adzuna_config() -> AdzunaConfig:
    """
    Load and validate Adzuna configuration from environment variables.

    Values can come from real environment variables or from a local .env file.
    """
    load_dotenv()

    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    country = os.getenv("ADZUNA_COUNTRY", "au").strip() or "au"

    if not app_id:
        raise RuntimeError(
            "ADZUNA_APP_ID is not set. "
            "Add it to a local .env file or export it in your terminal."
        )

    if not app_key:
        raise RuntimeError(
            "ADZUNA_APP_KEY is not set. "
            "Add it to a local .env file or export it in your terminal."
        )

    return AdzunaConfig(
        app_id=app_id,
        app_key=app_key,
        country=country,
    )


def create_adzuna_source() -> AdzunaSource:
    """
    Create an AdzunaSource using validated environment configuration.
    """
    config = load_adzuna_config()

    return AdzunaSource(
        app_id=config.app_id,
        app_key=config.app_key,
        country=config.country,
    )