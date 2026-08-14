-- CareerVoice AI application users and persistent daily usage.
--
-- This schema intentionally avoids foreign keys to provider-specific
-- authentication tables such as Supabase auth.users. CareerVoice owns its
-- application user IDs and maps them to external authentication identities.
-- Atomically record a daily operation and, when applicable,
-- consume AI usage units.
--
-- p_units may be zero for non-AI operations such as job searches.
-- The daily AI quota is enforced only when p_units is greater than zero.

create or replace function public.consume_daily_usage(
    p_user_id uuid,
    p_usage_date date,
    p_units integer,
    p_daily_limit integer,
    p_operation text
)
returns table (
    allowed boolean,
    ai_units_used integer,
    remaining_ai_units integer
)
language plpgsql
security invoker
as $$
declare
    v_operation text;
    v_ai_units_used integer;
begin
    if p_user_id is null then
        raise exception 'User ID cannot be null.';
    end if;

    if p_usage_date is null then
        raise exception 'Usage date cannot be null.';
    end if;

    if p_units is null or p_units < 0 then
        raise exception 'Usage units must be zero or greater.';
    end if;

    if p_daily_limit is null or p_daily_limit < 0 then
        raise exception 'Daily usage limit must be zero or greater.';
    end if;

    if p_operation is null or btrim(p_operation) = '' then
        raise exception 'Usage operation cannot be empty.';
    end if;

    v_operation := lower(btrim(p_operation));

    if v_operation not in (
        'profile_extraction',
        'voice_transcription',
        'document_recognition',
        'ai_ranking',
        'job_search'
    ) then
        raise exception 'Unsupported usage operation: %', v_operation;
    end if;

    -- A request that individually costs more than the whole daily
    -- allowance can never be accepted.
    if p_units > p_daily_limit then
        select coalesce(du.ai_units_used, 0)
        into v_ai_units_used
        from public.daily_usage as du
        where du.user_id = p_user_id
          and du.usage_date = p_usage_date;

        v_ai_units_used := coalesce(v_ai_units_used, 0);

        return query
        select
            false,
            v_ai_units_used,
            greatest(p_daily_limit - v_ai_units_used, 0);

        return;
    end if;

    insert into public.daily_usage as du (
        user_id,
        usage_date,
        ai_units_used,
        ai_profile_extractions,
        voice_transcriptions,
        document_recognitions,
        ai_ranking_runs,
        job_searches
    )
    values (
        p_user_id,
        p_usage_date,
        p_units,
        case when v_operation = 'profile_extraction' then 1 else 0 end,
        case when v_operation = 'voice_transcription' then 1 else 0 end,
        case when v_operation = 'document_recognition' then 1 else 0 end,
        case when v_operation = 'ai_ranking' then 1 else 0 end,
        case when v_operation = 'job_search' then 1 else 0 end
    )
    on conflict (user_id, usage_date)
    do update
    set
        ai_units_used =
            du.ai_units_used + excluded.ai_units_used,

        ai_profile_extractions =
            du.ai_profile_extractions
            + excluded.ai_profile_extractions,

        voice_transcriptions =
            du.voice_transcriptions
            + excluded.voice_transcriptions,

        document_recognitions =
            du.document_recognitions
            + excluded.document_recognitions,

        ai_ranking_runs =
            du.ai_ranking_runs
            + excluded.ai_ranking_runs,

        job_searches =
            du.job_searches
            + excluded.job_searches,

        updated_at = now()

    -- Non-AI operations use zero units and remain recordable even if
    -- the AI allowance has already been exhausted.
    where
        excluded.ai_units_used = 0
        or (
            du.ai_units_used + excluded.ai_units_used
            <= p_daily_limit
        )

    returning du.ai_units_used
    into v_ai_units_used;

    if found then
        return query
        select
            true,
            v_ai_units_used,
            greatest(p_daily_limit - v_ai_units_used, 0);

        return;
    end if;

    -- No update occurred because the operation would exceed the quota.
    select coalesce(du.ai_units_used, 0)
    into v_ai_units_used
    from public.daily_usage as du
    where du.user_id = p_user_id
      and du.usage_date = p_usage_date;

    v_ai_units_used := coalesce(v_ai_units_used, 0);

    return query
    select
        false,
        v_ai_units_used,
        greatest(p_daily_limit - v_ai_units_used, 0);
end;
$$;


-- PostgreSQL grants EXECUTE on newly created functions to PUBLIC by
-- default. CareerVoice will explicitly grant access to its server-side
-- database role later.
revoke execute
on function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
from public;

create table public.app_users (
    id uuid primary key,
    email text not null,
    auth_provider text not null,
    auth_subject text not null,
    enabled boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint app_users_email_not_blank
        check (btrim(email) <> ''),

    constraint app_users_email_normalized
        check (email = lower(btrim(email))),

    constraint app_users_auth_provider_not_blank
        check (btrim(auth_provider) <> ''),

    constraint app_users_auth_provider_normalized
        check (auth_provider = lower(btrim(auth_provider))),

    constraint app_users_auth_subject_not_blank
        check (btrim(auth_subject) <> ''),

    constraint app_users_email_unique
        unique (email),

    constraint app_users_auth_identity_unique
        unique (auth_provider, auth_subject)
);


create table public.daily_usage (
    user_id uuid not null
        references public.app_users(id)
        on delete cascade,

    usage_date date not null,

    ai_units_used integer not null default 0,
    ai_profile_extractions integer not null default 0,
    voice_transcriptions integer not null default 0,
    document_recognitions integer not null default 0,
    ai_ranking_runs integer not null default 0,
    job_searches integer not null default 0,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    primary key (user_id, usage_date),

    constraint daily_usage_ai_units_nonnegative
        check (ai_units_used >= 0),

    constraint daily_usage_profile_extractions_nonnegative
        check (ai_profile_extractions >= 0),

    constraint daily_usage_voice_transcriptions_nonnegative
        check (voice_transcriptions >= 0),

    constraint daily_usage_document_recognitions_nonnegative
        check (document_recognitions >= 0),

    constraint daily_usage_ai_ranking_runs_nonnegative
        check (ai_ranking_runs >= 0),

    constraint daily_usage_job_searches_nonnegative
        check (job_searches >= 0)
);


alter table public.app_users enable row level security;
alter table public.daily_usage enable row level security;