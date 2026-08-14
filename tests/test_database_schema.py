from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "supabase"
    / "migrations"
    / "20260814191400_create_user_usage_schema.sql"
)


def _migration_sql() -> str:
    return MIGRATION.read_text(encoding="utf-8").lower()


def test_user_usage_migration_exists() -> None:
    assert MIGRATION.is_file()


def test_migration_creates_application_user_table() -> None:
    sql = _migration_sql()

    assert "create table public.app_users" in sql
    assert "id uuid primary key" in sql
    assert "auth_provider text not null" in sql
    assert "auth_subject text not null" in sql
    assert "enabled boolean not null default true" in sql


def test_migration_creates_daily_usage_table() -> None:
    sql = _migration_sql()

    assert "create table public.daily_usage" in sql
    assert "ai_units_used integer not null default 0" in sql
    assert "ai_profile_extractions integer not null default 0" in sql
    assert "voice_transcriptions integer not null default 0" in sql
    assert "document_recognitions integer not null default 0" in sql
    assert "ai_ranking_runs integer not null default 0" in sql
    assert "job_searches integer not null default 0" in sql


def test_daily_usage_has_per_user_per_day_primary_key() -> None:
    sql = _migration_sql()

    assert "primary key (user_id, usage_date)" in sql


def test_user_schema_does_not_depend_on_supabase_auth_tables() -> None:
    sql = _migration_sql()

    assert "references auth.users" not in sql
    assert "references auth.users(" not in sql


def test_schema_enables_row_level_security() -> None:
    sql = _migration_sql()

    assert "alter table public.app_users enable row level security;" in sql
    assert "alter table public.daily_usage enable row level security;" in sql


def test_migration_creates_atomic_usage_function() -> None:
    sql = _migration_sql()

    assert "create or replace function public.consume_daily_usage" in sql
    assert "on conflict (user_id, usage_date)" in sql
    assert "du.ai_units_used + excluded.ai_units_used" in sql
    assert "<= p_daily_limit" in sql


def test_usage_function_tracks_supported_operations() -> None:
    sql = _migration_sql()

    assert "'profile_extraction'" in sql
    assert "'voice_transcription'" in sql
    assert "'document_recognition'" in sql
    assert "'ai_ranking'" in sql
    assert "'job_search'" in sql


def test_usage_function_returns_quota_state() -> None:
    sql = _migration_sql()

    assert "allowed boolean" in sql
    assert "remaining_ai_units integer" in sql


def test_usage_function_does_not_grant_public_execution() -> None:
    sql = _migration_sql()

    assert "revoke execute" in sql
    assert "from public;" in sql