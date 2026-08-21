from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = (
    ROOT
    / "supabase"
    / "migrations"
)


def _runtime_migration() -> Path:
    matches = list(
        MIGRATIONS_DIR.glob(
            "*_restrict_runtime_database_access.sql"
        )
    )

    assert len(matches) == 1

    return matches[0]


def _sql() -> str:
    return _runtime_migration().read_text(
        encoding="utf-8"
    ).lower()


def test_runtime_database_role_is_non_login() -> None:
    sql = _sql()

    assert (
        "create role careervoice_runtime nologin"
        in sql
    )


def test_runtime_role_has_no_direct_table_access() -> None:
    sql = _sql()

    assert (
        "on table public.app_users"
        in sql
    )
    assert (
        "on table public.daily_usage"
        in sql
    )
    assert (
        "from careervoice_runtime"
        in sql
    )

    assert (
        "grant select on table public.app_users"
        not in sql
    )
    assert (
        "grant select on table public.daily_usage"
        not in sql
    )
    assert (
        "grant insert on table public.daily_usage"
        not in sql
    )
    assert (
        "grant update on table public.daily_usage"
        not in sql
    )


def test_runtime_lookup_functions_are_security_definer() -> None:
    sql = _sql()

    assert (
        "function public.find_app_user_by_identity"
        in sql
    )
    assert (
        "function public.get_daily_usage"
        in sql
    )

    assert sql.count(
        "security definer"
    ) >= 3

    assert sql.count(
        "search_path = pg_catalog, public"
    ) >= 3


def test_atomic_usage_function_becomes_security_definer() -> None:
    sql = _sql()

    assert (
        "alter function public.consume_daily_usage"
        in sql
    )
    assert "security definer;" in sql


def test_runtime_role_only_receives_function_execution() -> None:
    sql = _sql()

    assert (
        "to careervoice_runtime"
        in sql
    )

    assert (
        "find_app_user_by_identity(text, text)"
        in sql
    )

    assert (
        "get_daily_usage(uuid, date)"
        in sql
    )

    assert (
        "consume_daily_usage("
        in sql
    )


def test_runtime_migration_contains_no_password() -> None:
    sql = _sql()

    assert "password" not in sql