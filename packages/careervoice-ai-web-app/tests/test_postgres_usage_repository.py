from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pytest

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)
from careervoice_ai_web_app.user_models import AppUser


class FakeCursor:
    def __init__(
        self,
        *,
        row: dict[str, Any] | None = None,
    ) -> None:
        self.row = row
        self.executions: list[
            tuple[str, tuple[object, ...]]
        ] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None

    def execute(
        self,
        query: str,
        params: tuple[object, ...],
    ) -> None:
        self.executions.append(
            (
                " ".join(query.split()),
                params,
            )
        )

    def fetchone(self) -> dict[str, Any] | None:
        return self.row


class FakeConnection:
    def __init__(
        self,
        *,
        row: dict[str, Any] | None = None,
    ) -> None:
        self.cursor_instance = FakeCursor(row=row)

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None

    def cursor(
        self,
        *,
        row_factory: object | None = None,
    ) -> FakeCursor:
        return self.cursor_instance


def _user() -> AppUser:
    return AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )


def test_get_daily_usage_returns_persisted_row() -> None:
    user = _user()
    usage_date = date(2026, 8, 21)

    connection = FakeConnection(
        row={
            "user_id": user.id,
            "usage_date": usage_date,
            "ai_units_used": 7,
            "ai_profile_extractions": 2,
            "voice_transcriptions": 1,
            "document_recognitions": 1,
            "ai_ranking_runs": 3,
            "job_searches": 4,
        }
    )

    repository = PostgresPersistentUsageRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    usage = repository.get_daily_usage(
        user=user,
        usage_date=usage_date,
    )

    assert usage == DailyUsageSnapshot(
        user_id=user.id,
        usage_date=usage_date,
        ai_units_used=7,
        ai_profile_extractions=2,
        voice_transcriptions=1,
        document_recognitions=1,
        ai_ranking_runs=3,
        job_searches=4,
    )


def test_get_daily_usage_returns_zero_snapshot_when_missing() -> None:
    user = _user()
    usage_date = date(2026, 8, 21)

    repository = PostgresPersistentUsageRepository(
        lambda: FakeConnection(row=None)  # type: ignore[arg-type]
    )

    usage = repository.get_daily_usage(
        user=user,
        usage_date=usage_date,
    )

    assert usage.ai_units_used == 0
    assert usage.job_searches == 0
    assert usage.user_id == user.id
    assert usage.usage_date == usage_date


def test_consume_calls_atomic_database_function() -> None:
    user = _user()
    usage_date = date(2026, 8, 21)

    connection = FakeConnection(
        row={
            "allowed": True,
            "ai_units_used": 6,
            "remaining_ai_units": 14,
        }
    )

    repository = PostgresPersistentUsageRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    decision = repository.consume(
        user=user,
        usage_date=usage_date,
        units=2,
        daily_limit=20,
        operation=UsageOperation.AI_RANKING,
    )

    assert decision == UsageDecision(
        allowed=True,
        ai_units_used=6,
        remaining_ai_units=14,
    )

    query, params = connection.cursor_instance.executions[0]

    assert "public.consume_daily_usage" in query.lower()

    assert params == (
        user.id,
        usage_date,
        2,
        20,
        "ai_ranking",
    )


def test_consume_returns_rejected_decision() -> None:
    user = _user()

    repository = PostgresPersistentUsageRepository(
        lambda: FakeConnection(
            row={
                "allowed": False,
                "ai_units_used": 20,
                "remaining_ai_units": 0,
            }
        )  # type: ignore[arg-type]
    )

    decision = repository.consume(
        user=user,
        usage_date=date(2026, 8, 21),
        units=1,
        daily_limit=20,
        operation=UsageOperation.PROFILE_EXTRACTION,
    )

    assert decision.allowed is False
    assert decision.ai_units_used == 20
    assert decision.remaining_ai_units == 0


@pytest.mark.parametrize(
    ("units", "daily_limit", "message"),
    [
        (-1, 20, "Usage units"),
        (1, -1, "Daily usage limit"),
    ],
)
def test_consume_rejects_invalid_limits(
    units: int,
    daily_limit: int,
    message: str,
) -> None:
    repository = PostgresPersistentUsageRepository(
        lambda: FakeConnection()  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match=message,
    ):
        repository.consume(
            user=_user(),
            usage_date=date(2026, 8, 21),
            units=units,
            daily_limit=daily_limit,
            operation=UsageOperation.AI_RANKING,
        )


def test_consume_requires_database_result() -> None:
    repository = PostgresPersistentUsageRepository(
        lambda: FakeConnection(row=None)  # type: ignore[arg-type]
    )

    with pytest.raises(
        RuntimeError,
        match="returned no quota result",
    ):
        repository.consume(
            user=_user(),
            usage_date=date(2026, 8, 21),
            units=1,
            daily_limit=20,
            operation=UsageOperation.AI_RANKING,
        )