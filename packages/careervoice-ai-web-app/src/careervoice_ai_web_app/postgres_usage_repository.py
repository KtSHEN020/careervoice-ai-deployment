"""PostgreSQL persistence for CareerVoice daily usage."""

from __future__ import annotations

from datetime import date

from psycopg.rows import dict_row

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    PersistentUsageRepository,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.postgres_user_repository import (
    ConnectionFactory,
)
from careervoice_ai_web_app.user_models import AppUser


class PostgresPersistentUsageRepository(PersistentUsageRepository):
    """Persist CareerVoice usage in PostgreSQL."""

    def __init__(
        self,
        connection_factory: ConnectionFactory,
    ) -> None:
        self._connection_factory = connection_factory

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        """Read persisted counters for a user and date."""
        with self._connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select
                        user_id,
                        usage_date,
                        ai_units_used,
                        ai_profile_extractions,
                        voice_transcriptions,
                        document_recognitions,
                        ai_ranking_runs,
                        job_searches
                    from public.daily_usage
                    where user_id = %s
                      and usage_date = %s
                    """,
                    (
                        user.id,
                        usage_date,
                    ),
                )

                row = cursor.fetchone()

        if row is None:
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

        return DailyUsageSnapshot(
            user_id=row["user_id"],
            usage_date=row["usage_date"],
            ai_units_used=row["ai_units_used"],
            ai_profile_extractions=row["ai_profile_extractions"],
            voice_transcriptions=row["voice_transcriptions"],
            document_recognitions=row["document_recognitions"],
            ai_ranking_runs=row["ai_ranking_runs"],
            job_searches=row["job_searches"],
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
        """Use the database's atomic quota function."""
        if units < 0:
            raise ValueError("Usage units must be zero or greater.")

        if daily_limit < 0:
            raise ValueError("Daily usage limit must be zero or greater.")

        with self._connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select
                        allowed,
                        ai_units_used,
                        remaining_ai_units
                    from public.consume_daily_usage(
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user.id,
                        usage_date,
                        units,
                        daily_limit,
                        operation.value,
                    ),
                )

                row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Persistent usage database returned no quota result."
            )

        return UsageDecision(
            allowed=row["allowed"],
            ai_units_used=row["ai_units_used"],
            remaining_ai_units=row["remaining_ai_units"],
        )