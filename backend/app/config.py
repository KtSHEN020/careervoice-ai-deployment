"""Configuration for the CareerVoice AI backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


SUPPORTED_ENVIRONMENTS = {
    "development",
    "test",
    "production",
}

DEFAULT_DAILY_AI_UNIT_LIMIT = 40


@dataclass(frozen=True)
class BackendSettings:
    """Runtime settings for the CareerVoice AI API."""

    environment: str = "development"
    api_title: str = "CareerVoice AI API"
    api_version: str = "0.1.0"
    daily_ai_unit_limit: int = DEFAULT_DAILY_AI_UNIT_LIMIT

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> BackendSettings:
        """Build backend settings from environment variables."""
        env = os.environ if environment is None else environment

        app_environment = env.get(
            "CAREERVOICE_ENVIRONMENT",
            "development",
        ).strip().lower()

        if not app_environment:
            app_environment = "development"

        if app_environment not in SUPPORTED_ENVIRONMENTS:
            raise ValueError(
                "CAREERVOICE_ENVIRONMENT must be one of: "
                + ", ".join(sorted(SUPPORTED_ENVIRONMENTS))
                + "."
            )

        raw_daily_limit = env.get(
            "CAREERVOICE_DAILY_AI_UNIT_LIMIT",
            str(DEFAULT_DAILY_AI_UNIT_LIMIT),
        ).strip()

        try:
            daily_ai_unit_limit = int(raw_daily_limit)
        except ValueError as exc:
            raise ValueError(
                "CAREERVOICE_DAILY_AI_UNIT_LIMIT must be an integer."
            ) from exc

        if daily_ai_unit_limit <= 0:
            raise ValueError(
                "CAREERVOICE_DAILY_AI_UNIT_LIMIT must be greater than zero."
            )

        return cls(
            environment=app_environment,
            daily_ai_unit_limit=daily_ai_unit_limit,
        )