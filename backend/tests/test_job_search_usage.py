from __future__ import annotations

from datetime import date
from uuid import UUID

import pytest

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.job_search_usage import (
    PersistentJobSearchUsageRecorder,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


class FakeUsageRepository:
    def __init__(
        self,
        *,
        allowed: bool = True,
    ) -> None:
        self.allowed = allowed
        self.consume_calls: list[
            dict[str, object]
        ] = []

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        return DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=40,
            ai_profile_extractions=0,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=3,
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

        return UsageDecision(
            allowed=self.allowed,
            ai_units_used=40,
            remaining_ai_units=0,
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_job_search_recording_uses_zero_ai_units() -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)
    repository = FakeUsageRepository()

    recorder = PersistentJobSearchUsageRecorder(
        repository=repository,
        daily_ai_unit_limit=60,
        usage_date_factory=lambda: usage_date,
    )

    recorder.record_job_search(
        user=user
    )

    assert repository.consume_calls == [
        {
            "user": user,
            "usage_date": usage_date,
            "units": 0,
            "daily_limit": 60,
            "operation": UsageOperation.JOB_SEARCH,
        }
    ]


def test_job_search_recording_can_occur_with_no_ai_units_remaining() -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)
    repository = FakeUsageRepository()

    recorder = PersistentJobSearchUsageRecorder(
        repository=repository,
        daily_ai_unit_limit=40,
        usage_date_factory=lambda: usage_date,
    )

    recorder.record_job_search(
        user=user
    )

    assert len(repository.consume_calls) == 1
    assert repository.consume_calls[0]["units"] == 0


def test_job_search_recording_rejects_unexpected_database_denial() -> None:
    repository = FakeUsageRepository(
        allowed=False
    )

    recorder = PersistentJobSearchUsageRecorder(
        repository=repository,
        daily_ai_unit_limit=40,
    )

    with pytest.raises(
        RuntimeError,
        match="unexpectedly rejected",
    ):
        recorder.record_job_search(
            user=create_user()
        )


@pytest.mark.parametrize(
    "daily_ai_unit_limit",
    [
        0,
        -1,
        True,
    ],
)
def test_job_search_recorder_requires_positive_limit(
    daily_ai_unit_limit: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        PersistentJobSearchUsageRecorder(
            repository=FakeUsageRepository(),
            daily_ai_unit_limit=daily_ai_unit_limit,  # type: ignore[arg-type]
        )