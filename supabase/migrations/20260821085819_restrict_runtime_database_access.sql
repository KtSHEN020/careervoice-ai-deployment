do $$
begin
    if not exists (
        select 1
        from pg_catalog.pg_roles
        where rolname = 'careervoice_runtime'
    ) then
        create role careervoice_runtime nologin;
    end if;
end
$$;

create or replace function public.find_app_user_by_identity(
    p_auth_provider text,
    p_auth_subject text
)
returns table (
    id uuid,
    email text,
    auth_provider text,
    auth_subject text,
    enabled boolean
)
language sql
stable
security definer
set search_path = pg_catalog, public
as $function$
    select
        u.id,
        u.email,
        u.auth_provider,
        u.auth_subject,
        u.enabled
    from public.app_users as u
    where u.auth_provider = p_auth_provider
      and u.auth_subject = p_auth_subject
    limit 1;
$function$;

create or replace function public.get_daily_usage(
    p_user_id uuid,
    p_usage_date date
)
returns table (
    user_id uuid,
    usage_date date,
    ai_units_used integer,
    ai_profile_extractions integer,
    voice_transcriptions integer,
    document_recognitions integer,
    ai_ranking_runs integer,
    job_searches integer
)
language sql
stable
security definer
set search_path = pg_catalog, public
as $function$
    select
        d.user_id,
        d.usage_date,
        d.ai_units_used,
        d.ai_profile_extractions,
        d.voice_transcriptions,
        d.document_recognitions,
        d.ai_ranking_runs,
        d.job_searches
    from public.daily_usage as d
    where d.user_id = p_user_id
      and d.usage_date = p_usage_date
    limit 1;
$function$;

alter function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
security definer;

alter function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
set search_path = pg_catalog, public;

revoke execute
on function public.find_app_user_by_identity(text, text)
from public;

revoke execute
on function public.get_daily_usage(uuid, date)
from public;

revoke execute
on function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
from public;

revoke all
on schema public
from careervoice_runtime;

grant usage
on schema public
to careervoice_runtime;

revoke all
on table public.app_users
from careervoice_runtime;

revoke all
on table public.daily_usage
from careervoice_runtime;

grant execute
on function public.find_app_user_by_identity(text, text)
to careervoice_runtime;

grant execute
on function public.get_daily_usage(uuid, date)
to careervoice_runtime;

grant execute
on function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
to careervoice_runtime;