-- Make CareerVoice's atomic AI usage function honor the quota-exemption
-- flag stored on public.app_users.
--
-- Exempt users still accumulate all usage counters and AI units.
-- Only application-level quota rejection is bypassed.

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
security definer
set search_path = pg_catalog, public
as $function$
declare
    v_operation text;
    v_ai_units_used integer;
    v_ai_quota_exempt boolean;
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

    select u.ai_quota_exempt
    into v_ai_quota_exempt
    from public.app_users as u
    where u.id = p_user_id;

    if not found then
        raise exception 'CareerVoice user does not exist.';
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

    -- A non-exempt user cannot make one request that by itself costs
    -- more than the configured daily allowance.
    if (
        not v_ai_quota_exempt
        and p_units > p_daily_limit
    ) then
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
            greatest(
                p_daily_limit - v_ai_units_used,
                0
            );

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
        case
            when v_operation = 'profile_extraction'
            then 1
            else 0
        end,
        case
            when v_operation = 'voice_transcription'
            then 1
            else 0
        end,
        case
            when v_operation = 'document_recognition'
            then 1
            else 0
        end,
        case
            when v_operation = 'ai_ranking'
            then 1
            else 0
        end,
        case
            when v_operation = 'job_search'
            then 1
            else 0
        end
    )
    on conflict (user_id, usage_date)
    do update
    set
        ai_units_used =
            du.ai_units_used
            + excluded.ai_units_used,

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

    where
        v_ai_quota_exempt
        or excluded.ai_units_used = 0
        or (
            du.ai_units_used
            + excluded.ai_units_used
            <= p_daily_limit
        )

    returning du.ai_units_used
    into v_ai_units_used;

    if found then
        return query
        select
            true,
            v_ai_units_used,
            greatest(
                p_daily_limit - v_ai_units_used,
                0
            );

        return;
    end if;

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
        greatest(
            p_daily_limit - v_ai_units_used,
            0
        );
end;
$function$;


revoke execute
on function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
from public;


grant execute
on function public.consume_daily_usage(
    uuid,
    date,
    integer,
    integer,
    text
)
to careervoice_runtime;