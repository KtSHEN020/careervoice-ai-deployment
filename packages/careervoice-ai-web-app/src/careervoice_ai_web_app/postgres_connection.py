"""PostgreSQL connection configuration for CareerVoice AI."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg import Connection


@dataclass(frozen=True)
class PostgresConnectionSettings:
    """Server-side PostgreSQL connection settings."""

    host: str
    port: int
    dbname: str
    user: str
    password: str
    sslmode: str = "require"

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> PostgresConnectionSettings | None:
        """Load database settings without exposing credential values."""
        env = os.environ if environment is None else environment

        required_keys = (
            "DATABASE_HOST",
            "DATABASE_PORT",
            "DATABASE_NAME",
            "DATABASE_USER",
            "DATABASE_PASSWORD",
        )

        supplied = {
            key: env.get(key, "").strip()
            for key in required_keys
        }

        if not any(supplied.values()):
            return None

        missing = [
            key
            for key, value in supplied.items()
            if not value
        ]

        if missing:
            raise ValueError(
                "Database configuration is incomplete. "
                "Missing: "
                + ", ".join(missing)
            )

        try:
            port = int(supplied["DATABASE_PORT"])
        except ValueError as exc:
            raise ValueError(
                "DATABASE_PORT must be an integer."
            ) from exc

        if not 1 <= port <= 65535:
            raise ValueError(
                "DATABASE_PORT must be between 1 and 65535."
            )

        sslmode = env.get(
            "DATABASE_SSLMODE",
            "require",
        ).strip()

        if not sslmode:
            sslmode = "require"

        return cls(
            host=supplied["DATABASE_HOST"],
            port=port,
            dbname=supplied["DATABASE_NAME"],
            user=supplied["DATABASE_USER"],
            password=supplied["DATABASE_PASSWORD"],
            sslmode=sslmode,
        )


def build_postgres_connection_factory(
    settings: PostgresConnectionSettings,
) -> Callable[[], Connection[Any]]:
    """Build a lazy PostgreSQL connection factory."""

    def connection_factory() -> Connection[Any]:
        return psycopg.connect(
            host=settings.host,
            port=settings.port,
            dbname=settings.dbname,
            user=settings.user,
            password=settings.password,
            sslmode=settings.sslmode,
            connect_timeout=10,
        )

    return connection_factory