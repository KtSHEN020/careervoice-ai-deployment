"""Daily usage status for the CareerVoice AI backend."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
)
from careervoice_ai_web_app.user_models import AppUser


def _utc_today() -> date:
    """Return the current UTC calendar date."""
    return datetime.now(UTC).date()


class DailyUsageReader(Protocol):
    """Read persistent usage for one CareerVoice user."""

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        """Return usage counters for a user and date."""
        ...


class DailyUsageStatusProvider(Protocol):
    """Provide daily usage status for one CareerVoice user."""

    def get_status(
        self,
        user: AppUser,
    ) -> DailyUsageStatus:
        """Return today's usage status."""
        ...


@dataclass(frozen=True)
class DailyUsageStatus:
    """Daily usage information exposed by the backend."""

    usage_date: date
    daily_ai_unit_limit: int
    ai_quota_exempt: bool
    ai_units_used: int
    remaining_ai_units: int | None
    ai_profile_extractions: int
    voice_transcriptions: int
    document_recognitions: int
    ai_ranking_runs: int
    job_searches: int


@dataclass
class DailyUsageService:
    """Read daily usage using the backend's configured AI allowance."""

    repository: DailyUsageReader
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

    def get_status(
        self,
        user: AppUser,
    ) -> DailyUsageStatus:
        """Return today's usage status for a CareerVoice user."""
        usage_date = self.usage_date_factory()

        usage = self.repository.get_daily_usage(
            user=user,
            usage_date=usage_date,
        )

        remaining_ai_units = (
            None
            if user.ai_quota_exempt
            else max(
                0,
                self.daily_ai_unit_limit
                - usage.ai_units_used,
            )
        )

        return DailyUsageStatus(
            usage_date=usage_date,
            daily_ai_unit_limit=self.daily_ai_unit_limit,
            ai_quota_exempt=user.ai_quota_exempt,
            ai_units_used=usage.ai_units_used,
            remaining_ai_units=remaining_ai_units,
            ai_profile_extractions=(
                usage.ai_profile_extractions
            ),
            voice_transcriptions=(
                usage.voice_transcriptions
            ),
            document_recognitions=(
                usage.document_recognitions
            ),
            ai_ranking_runs=usage.ai_ranking_runs,
            job_searches=usage.job_searches,
        )