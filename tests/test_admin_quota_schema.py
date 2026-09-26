from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MIGRATION = (
    ROOT
    / "supabase"
    / "migrations"
    / "20260925130500_add_ai_quota_exemption.sql"
)

QUOTA_MIGRATION = (
    ROOT
    / "supabase"
    / "migrations"
    / "20260925140000_honor_ai_quota_exemption.sql"
)


def _quota_sql() -> str:
    return QUOTA_MIGRATION.read_text(
        encoding="utf-8"
    ).lower()

def _sql() -> str:
    return MIGRATION.read_text(
        encoding="utf-8"
    ).lower()


def test_admin_quota_migration_exists() -> None:
    assert MIGRATION.is_file()


def test_migration_adds_quota_exemption() -> None:
    sql = _sql()

    assert (
        "ai_quota_exempt boolean not null default false"
        in sql
    )


def test_identity_lookup_returns_quota_exemption() -> None:
    sql = _sql()

    assert (
        "function public.find_app_user_by_identity"
        in sql
    )
    assert "ai_quota_exempt boolean" in sql
    assert "u.ai_quota_exempt" in sql


def test_identity_lookup_remains_security_definer() -> None:
    sql = _sql()

    assert "security definer" in sql
    assert (
        "search_path = pg_catalog, public"
        in sql
    )


def test_identity_lookup_is_not_publicly_executable() -> None:
    sql = _sql()

    assert "revoke execute" in sql
    assert "from public;" in sql


def test_runtime_role_can_execute_identity_lookup() -> None:
    sql = _sql()

    assert (
        "find_app_user_by_identity(text, text)"
        in sql
    )
    assert "to careervoice_runtime;" in sql


def test_quota_exemption_migration_exists() -> None:
    assert QUOTA_MIGRATION.is_file()


def test_quota_function_reads_exemption_from_app_users() -> None:
    sql = _quota_sql()

    assert "u.ai_quota_exempt" in sql
    assert "from public.app_users" in sql


def test_quota_function_does_not_trust_caller_for_exemption() -> None:
    sql = _quota_sql()

    assert "p_ai_quota_exempt" not in sql
    assert "p_quota_exempt" not in sql


def test_exempt_users_bypass_daily_limit_check() -> None:
    sql = _quota_sql()

    assert "not v_ai_quota_exempt" in sql
    assert "p_units > p_daily_limit" in sql


def test_exempt_users_can_still_update_usage() -> None:
    sql = _quota_sql()

    assert "v_ai_quota_exempt" in sql
    assert "du.ai_units_used" in sql
    assert "+ excluded.ai_units_used" in sql


def test_quota_function_remains_security_definer() -> None:
    sql = _quota_sql()

    assert "security definer" in sql
    assert (
        "search_path = pg_catalog, public"
        in sql
    )


def test_quota_function_is_not_publicly_executable() -> None:
    sql = _quota_sql()

    assert "revoke execute" in sql
    assert "from public;" in sql


def test_runtime_role_can_execute_quota_function() -> None:
    sql = _quota_sql()

    assert "to careervoice_runtime;" in sql