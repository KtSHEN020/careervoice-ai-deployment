from datetime import date
from uuid import uuid4

import pytest

from careervoice_ai_web_app.ai_usage import AIUsageLimitError, AIUsageStatus
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser


class FakeUsageRepository:
    def __init__(
        self,
        decision: UsageDecision,
        *,
        snapshot: DailyUsageSnapshot | None = None,
    ) -> None:
        self.decision = decision
        self.snapshot = snapshot

        self.consume_calls: list[
            dict[str, object]
        ] = []

        self.get_calls: list[
            dict[str, object]
        ] = []

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        self.get_calls.append(
            {
                "user": user,
                "usage_date": usage_date,
            }
        )

        if self.snapshot is not None:
            return self.snapshot

        return DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=0,
            ai_profile_extractions=0,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=0,
        )

    def consume(
        self,
        *,
        user: AppUser,
        usage_date: date,
        units: int,
        daily_limit: int,
        operation: UsageOperation,
    ) -> UsageDecision:
        self.consume_calls.append(
            {
                "user": user,
                "usage_date": usage_date,
                "units": units,
                "daily_limit": daily_limit,
                "operation": operation,
            }
        )

        return self.decision


def _user() -> AppUser:
    return AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )


def test_persistent_budget_reserves_usage() -> None:
    user = _user()
    usage_date = date(2026, 8, 21)

    repository = FakeUsageRepository(
        UsageDecision(
            allowed=True,
            ai_units_used=11,
            remaining_ai_units=9,
        )
    )

    budget = PersistentAIUsageBudget(
        repository=repository,  # type: ignore[arg-type]
        user=user,
        usage_date_factory=lambda: usage_date,
    )

    budget.reserve(
        10,
        feature="AI-assisted job ranking",
        operation=UsageOperation.AI_RANKING,
    )

    assert repository.consume_calls == [
        {
            "user": user,
            "usage_date": usage_date,
            "units": 10,
            "daily_limit": 20,
            "operation": UsageOperation.AI_RANKING,
        }
    ]


def test_persistent_budget_rejects_exhausted_allowance() -> None:
    repository = FakeUsageRepository(
        UsageDecision(
            allowed=False,
            ai_units_used=20,
            remaining_ai_units=0,
        )
    )

    budget = PersistentAIUsageBudget(
        repository=repository,  # type: ignore[arg-type]
        user=_user(),
        usage_date_factory=lambda: date(2026, 8, 21),
    )

    with pytest.raises(
        AIUsageLimitError,
        match="daily AI allowance",
    ):
        budget.reserve(
            1,
            feature="AI-assisted profile creation",
            operation=UsageOperation.PROFILE_EXTRACTION,
        )


def test_persistent_budget_requires_operation() -> None:
    repository = FakeUsageRepository(
        UsageDecision(
            allowed=True,
            ai_units_used=1,
            remaining_ai_units=19,
        )
    )

    budget = PersistentAIUsageBudget(
        repository=repository,  # type: ignore[arg-type]
        user=_user(),
    )

    with pytest.raises(
        ValueError,
        match="requires a tracked operation",
    ):
        budget.reserve(
            1,
            feature="AI-assisted profile creation",
        )

    assert repository.consume_calls == []


@pytest.mark.parametrize(
    "units",
    [
        0,
        -1,
        True,
    ],
)
def test_persistent_budget_requires_positive_units(
    units: object,
) -> None:
    repository = FakeUsageRepository(
        UsageDecision(
            allowed=True,
            ai_units_used=1,
            remaining_ai_units=19,
        )
    )

    budget = PersistentAIUsageBudget(
        repository=repository,  # type: ignore[arg-type]
        user=_user(),
    )

    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        budget.reserve(
            units,  # type: ignore[arg-type]
            feature="AI-assisted profile creation",
            operation=UsageOperation.PROFILE_EXTRACTION,
        )


def test_persistent_budget_requires_positive_limit() -> None:
    repository = FakeUsageRepository(
        UsageDecision(
            allowed=True,
            ai_units_used=0,
            remaining_ai_units=0,
        )
    )

    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        PersistentAIUsageBudget(
            repository=repository,  # type: ignore[arg-type]
            user=_user(),
            limit=0,
        )


def test_persistent_budget_reports_database_status() -> None:
    user = _user()
    usage_date = date(2026, 8, 29)

    repository = FakeUsageRepository(
        UsageDecision(
            allowed=True,
            ai_units_used=7,
            remaining_ai_units=13,
        ),
        snapshot=DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=7,
            ai_profile_extractions=2,
            voice_transcriptions=1,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=3,
        ),
    )

    budget = PersistentAIUsageBudget(
        repository=repository,  # type: ignore[arg-type]
        user=user,
        usage_date_factory=lambda: usage_date,
    )

    assert budget.status() == AIUsageStatus(
        limit=20,
        used=7,
        remaining=13,
        profile_extractions=2,
        voice_transcriptions=1,
        document_recognitions=0,
        ai_ranking_runs=0,
    )

    assert repository.get_calls == [
        {
            "user": user,
            "usage_date": usage_date,
        }
    ]