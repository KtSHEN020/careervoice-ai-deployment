"""Persistent usage recording for CareerVoice job searches."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime

from careervoice_ai_web_app.persistent_usage import (
    PersistentUsageRepository,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser


def _utc_today() -> date:
    """Return the current UTC calendar date."""
    return datetime.now(UTC).date()


@dataclass
class PersistentJobSearchUsageRecorder:
    """Record successful job searches without consuming AI units."""

    repository: PersistentUsageRepository
    daily_ai_unit_limit: int
    usage_date_factory: Callable[[], date] = _utc_today

    def __post_init__(self) -> None:
        if (
            not isinstance(self.daily_ai_unit_limit, int)
            or isinstance(self.daily_ai_unit_limit, bool)
            or self.daily_ai_unit_limit <= 0
        ):
            raise ValueError(
                "Daily AI unit limit must be a positive integer."
            )

    def record_job_search(
        self,
        *,
        user: AppUser,
    ) -> None:
        """Record one successful job search at zero AI units."""
        decision = self.repository.consume(
            user=user,
            usage_date=self.usage_date_factory(),
            units=0,
            daily_limit=self.daily_ai_unit_limit,
            operation=UsageOperation.JOB_SEARCH,
        )

        if not decision.allowed:
            raise RuntimeError(
                "Job-search usage recording was unexpectedly rejected."
            )