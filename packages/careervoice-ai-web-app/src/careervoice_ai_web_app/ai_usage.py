"""Safeguards for AI-assisted application features."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Protocol

from careervoice_ai_web_app.persistent_usage import UsageOperation

AI_USAGE_UNITS_KEY = "ai_usage_units"

MAX_AI_USAGE_UNITS_PER_DAY = 40

# Keep the existing name for compatibility with the current
# session-based implementation and tests.
MAX_AI_USAGE_UNITS_PER_SESSION = MAX_AI_USAGE_UNITS_PER_DAY

PROFILE_EXTRACTION_AI_UNITS = 1
VOICE_TRANSCRIPTION_AI_UNITS = 1
DOCUMENT_RECOGNITION_AI_UNITS = 1
AI_RANKING_AI_UNITS = 10

@dataclass(frozen=True)
class AIUsageStatus:
    """Current AI allowance and per-feature usage visible to the user."""

    limit: int
    used: int
    remaining: int
    profile_extractions: int = 0
    voice_transcriptions: int = 0
    document_recognitions: int = 0
    ai_ranking_runs: int = 0


class AIUsageLimitError(ValueError):
    """Raised when an AI-assisted action exceeds its allowance."""


class SupportsAIUsageBudget(Protocol):
    """AI allowance interface required by the workflow service."""
    def status(self) -> AIUsageStatus:
        """Return the current AI allowance status."""
        ...

    def reserve(
        self,
        units: int,
        *,
        feature: str,
        operation: UsageOperation | None = None,
    ) -> None:
        """Reserve usage before an AI-assisted operation begins."""
        ...


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

    def status(self) -> AIUsageStatus:
        """Return the current session allowance."""
        return AIUsageStatus(
            limit=self.limit,
            used=self.used,
            remaining=self.remaining,
        )

    def reserve(
        self,
        units: int,
        *,
        feature: str,
        operation: UsageOperation | None = None,
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