"""Persistent per-user AI usage safeguards for CareerVoice AI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime

from careervoice_ai_web_app.ai_usage import (
    MAX_AI_USAGE_UNITS_PER_DAY,
    AIUsageLimitError,
)
from careervoice_ai_web_app.persistent_usage import (
    PersistentUsageRepository,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser


def _utc_today() -> date:
    """Return the current UTC calendar date."""
    return datetime.now(UTC).date()


@dataclass
class PersistentAIUsageBudget:
    """Enforce one persistent daily AI allowance for a CareerVoice user."""

    repository: PersistentUsageRepository
    user: AppUser
    limit: int = MAX_AI_USAGE_UNITS_PER_DAY
    usage_date_factory: Callable[[], date] = _utc_today

    def __post_init__(self) -> None:
        if (
            not isinstance(self.limit, int)
            or isinstance(self.limit, bool)
            or self.limit < 1
        ):
            raise ValueError(
                "AI usage limit must be a positive integer."
            )

    def reserve(
        self,
        units: int,
        *,
        feature: str,
        operation: UsageOperation | None = None,
    ) -> None:
        """Atomically reserve persistent allowance before an AI action."""
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

        if not isinstance(operation, UsageOperation):
            raise ValueError(
                "Persistent AI usage requires a tracked operation."
            )

        decision = self.repository.consume(
            user=self.user,
            usage_date=self.usage_date_factory(),
            units=units,
            daily_limit=self.limit,
            operation=operation,
        )

        if not decision.allowed:
            raise AIUsageLimitError(
                "This account does not have enough daily AI allowance "
                f"remaining for {cleaned_feature}. "
                "Standard non-AI features are still available."
            )