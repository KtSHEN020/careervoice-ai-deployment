from __future__ import annotations

from typing import Any
from uuid import uuid4

from careervoice_ai_web_app.postgres_user_repository import (
    PostgresAppUserRepository,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)


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
        self.row_factory_seen: object | None = None

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
        self.row_factory_seen = row_factory
        return self.cursor_instance


def _identity() -> AuthenticatedIdentity:
    return AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )


def _user() -> AppUser:
    return AppUser(
        id=uuid4(),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )


def test_find_by_identity_returns_user() -> None:
    user_id = uuid4()

    connection = FakeConnection(
        row={
            "id": user_id,
            "email": "tester@example.com",
            "auth_provider": "supabase",
            "auth_subject": "auth-user-123",
            "enabled": True,
        }
    )

    repository = PostgresAppUserRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    user = repository.find_by_identity(_identity())

    assert user == AppUser(
        id=user_id,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )

    query, params = connection.cursor_instance.executions[0]

    assert "from public.app_users" in query.lower()
    assert "auth_provider = %s" in query.lower()
    assert "auth_subject = %s" in query.lower()

    assert params == (
        "supabase",
        "auth-user-123",
    )


def test_find_by_identity_returns_none_when_missing() -> None:
    connection = FakeConnection(row=None)

    repository = PostgresAppUserRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    assert repository.find_by_identity(_identity()) is None


def test_add_inserts_user() -> None:
    connection = FakeConnection()

    repository = PostgresAppUserRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    user = _user()

    repository.add(user)

    query, params = connection.cursor_instance.executions[0]

    assert "insert into public.app_users" in query.lower()

    assert params == (
        user.id,
        user.email,
        user.auth_provider,
        user.auth_subject,
        True,
    )


def test_set_enabled_updates_user() -> None:
    connection = FakeConnection()

    repository = PostgresAppUserRepository(
        lambda: connection  # type: ignore[arg-type]
    )

    user = _user()

    repository.set_enabled(
        user,
        enabled=False,
    )

    query, params = connection.cursor_instance.executions[0]

    assert "update public.app_users" in query.lower()
    assert "updated_at = now()" in query.lower()

    assert params == (
        False,
        user.id,
    )