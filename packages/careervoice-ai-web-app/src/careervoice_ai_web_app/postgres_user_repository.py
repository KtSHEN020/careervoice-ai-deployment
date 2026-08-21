"""PostgreSQL persistence for CareerVoice application users."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row

from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)

ConnectionFactory = Callable[[], Connection[Any]]


class PostgresAppUserRepository:
    """Store and retrieve CareerVoice users from PostgreSQL."""

    def __init__(
        self,
        connection_factory: ConnectionFactory,
    ) -> None:
        self._connection_factory = connection_factory

    def find_by_identity(
        self,
        identity: AuthenticatedIdentity,
    ) -> AppUser | None:
        """Find a CareerVoice user by external authentication identity."""
        with self._connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select
                        id,
                        email,
                        auth_provider,
                        auth_subject,
                        enabled
                    from public.find_app_user_by_identity(
                        %s,
                        %s
                    )
                    """,
                    (
                        identity.provider,
                        identity.subject,
                    ),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return AppUser(
            id=row["id"],
            email=row["email"],
            auth_provider=row["auth_provider"],
            auth_subject=row["auth_subject"],
            enabled=row["enabled"],
        )

    def add(
        self,
        user: AppUser,
    ) -> None:
        """Insert a CareerVoice user."""
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into public.app_users (
                        id,
                        email,
                        auth_provider,
                        auth_subject,
                        enabled
                    )
                    values (%s, %s, %s, %s, %s)
                    """,
                    (
                        user.id,
                        user.email,
                        user.auth_provider,
                        user.auth_subject,
                        user.enabled,
                    ),
                )

    def set_enabled(
        self,
        user: AppUser,
        *,
        enabled: bool,
    ) -> None:
        """Enable or disable an existing CareerVoice user."""
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update public.app_users
                    set
                        enabled = %s,
                        updated_at = now()
                    where id = %s
                    """,
                    (
                        enabled,
                        user.id,
                    ),
                )