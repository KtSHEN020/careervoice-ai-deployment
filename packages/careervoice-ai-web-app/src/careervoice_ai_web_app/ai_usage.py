"""Session-level safeguards for AI-assisted application features."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass

AI_USAGE_UNITS_KEY = "ai_usage_units"

MAX_AI_USAGE_UNITS_PER_SESSION = 20

PROFILE_EXTRACTION_AI_UNITS = 1
VOICE_TRANSCRIPTION_AI_UNITS = 1
DOCUMENT_RECOGNITION_AI_UNITS = 1
AI_RANKING_AI_UNITS = 10


class AIUsageLimitError(ValueError):
    """Raised when an AI-assisted action exceeds the session allowance."""


def _stored_usage(
    state: MutableMapping[str, object],
) -> int:
    """Return a safe non-negative session usage value."""
    value = state.get(
        AI_USAGE_UNITS_KEY,
        0,
    )

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        return 0

    return value


@dataclass
class SessionAIUsageBudget:
    """Track and enforce AI usage within one application session."""

    state: MutableMapping[str, object]
    limit: int = MAX_AI_USAGE_UNITS_PER_SESSION

    def __post_init__(self) -> None:
        if (
            not isinstance(self.limit, int)
            or isinstance(self.limit, bool)
            or self.limit < 1
        ):
            raise ValueError(
                "AI usage limit must be a positive integer."
            )

    @property
    def used(self) -> int:
        """Return AI allowance already reserved in this session."""
        return _stored_usage(self.state)

    @property
    def remaining(self) -> int:
        """Return the unused AI allowance for this session."""
        return max(
            0,
            self.limit - self.used,
        )

    def reserve(
        self,
        units: int,
        *,
        feature: str,
    ) -> None:
        """Reserve allowance before an AI-assisted operation begins."""
        if (
            not isinstance(units, int)
            or isinstance(units, bool)
            or units < 1
        ):
            raise ValueError(
                "AI usage units must be a positive integer."
            )

        cleaned_feature = feature.strip()

        if not cleaned_feature:
            raise ValueError(
                "AI usage feature name cannot be empty."
            )

        if units > self.remaining:
            raise AIUsageLimitError(
                "This session does not have enough AI allowance remaining "
                f"for {cleaned_feature}. "
                "Standard non-AI features are still available."
            )

        self.state[AI_USAGE_UNITS_KEY] = (
            self.used + units
        )