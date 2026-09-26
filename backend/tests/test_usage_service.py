from __future__ import annotations

from datetime import date
from uuid import UUID

import pytest

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.usage_service import (
    DailyUsageService,
    DailyUsageStatus,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


class FakeDailyUsageReader:
    def __init__(
        self,
        snapshot: DailyUsageSnapshot,
    ) -> None:
        self.snapshot = snapshot

        self.calls: list[
            dict[str, object]
        ] = []

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        self.calls.append(
            {
                "user": user,
                "usage_date": usage_date,
            }
        )

        return self.snapshot


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def test_usage_service_returns_daily_status() -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)

    repository = FakeDailyUsageReader(
        DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=11,
            ai_profile_extractions=1,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=1,
            job_searches=3,
        )
    )

    service = DailyUsageService(
        repository=repository,
        daily_ai_unit_limit=40,
        usage_date_factory=lambda: usage_date,
    )

    assert service.get_status(
        user
    ) == DailyUsageStatus(
        usage_date=usage_date,
        daily_ai_unit_limit=40,
        ai_quota_exempt=False,
        ai_units_used=11,
        remaining_ai_units=29,
        ai_profile_extractions=1,
        voice_transcriptions=0,
        document_recognitions=0,
        ai_ranking_runs=1,
        job_searches=3,
    )

    assert repository.calls == [
        {
            "user": user,
            "usage_date": usage_date,
        }
    ]


def test_usage_service_uses_configured_limit() -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)

    repository = FakeDailyUsageReader(
        DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=11,
            ai_profile_extractions=1,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=1,
            job_searches=3,
        )
    )

    service = DailyUsageService(
        repository=repository,
        daily_ai_unit_limit=60,
        usage_date_factory=lambda: usage_date,
    )

    status = service.get_status(
        user
    )

    assert status.daily_ai_unit_limit == 60
    assert status.ai_units_used == 11
    assert status.remaining_ai_units == 49


def test_usage_service_never_reports_negative_remaining_units() -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)

    repository = FakeDailyUsageReader(
        DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=45,
            ai_profile_extractions=5,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=4,
            job_searches=3,
        )
    )

    service = DailyUsageService(
        repository=repository,
        daily_ai_unit_limit=40,
        usage_date_factory=lambda: usage_date,
    )

    assert (
        service.get_status(user).remaining_ai_units
        == 0
    )


@pytest.mark.parametrize(
    "daily_ai_unit_limit",
    [
        0,
        -1,
        True,
    ],
)
def test_usage_service_requires_positive_limit(
    daily_ai_unit_limit: object,
) -> None:
    user = create_user()
    usage_date = date(2026, 9, 12)

    repository = FakeDailyUsageReader(
        DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=0,
            ai_profile_extractions=0,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=0,
        )
    )

    with pytest.raises(
        ValueError,
        match="positive integer",
    ):
        DailyUsageService(
            repository=repository,
            daily_ai_unit_limit=daily_ai_unit_limit,  # type: ignore[arg-type]
        )


def test_usage_service_reports_quota_exempt_user_as_unlimited() -> None:
    usage_date = date(2026, 9, 12)

    user = AppUser(
        id=TEST_USER_ID,
        email="admin@example.com",
        auth_provider="supabase",
        auth_subject="provider-admin-123",
        enabled=True,
        ai_quota_exempt=True,
    )

    repository = FakeDailyUsageReader(
        DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=75,
            ai_profile_extractions=5,
            voice_transcriptions=2,
            document_recognitions=1,
            ai_ranking_runs=6,
            job_searches=8,
        )
    )

    service = DailyUsageService(
        repository=repository,
        daily_ai_unit_limit=40,
        usage_date_factory=lambda: usage_date,
    )

    status = service.get_status(user)

    assert status.daily_ai_unit_limit == 40
    assert status.ai_quota_exempt is True
    assert status.ai_units_used == 75
    assert status.remaining_ai_units is None