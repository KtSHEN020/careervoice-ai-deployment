-- Add explicit AI quota exemption for trusted CareerVoice accounts.
--
-- This flag affects only CareerVoice's application-level AI quota.
-- Usage should continue to be recorded for exempt users.

alter table public.app_users
add column ai_quota_exempt boolean not null default false;


-- The function's RETURNS TABLE shape is changing, so PostgreSQL
-- requires it to be recreated rather than replaced in place.
drop function public.find_app_user_by_identity(text, text);


create function public.find_app_user_by_identity(
    p_auth_provider text,
    p_auth_subject text
)
returns table (
    id uuid,
    email text,
    auth_provider text,
    auth_subject text,
    enabled boolean,
    ai_quota_exempt boolean
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
        u.enabled,
        u.ai_quota_exempt
    from public.app_users as u
    where u.auth_provider = p_auth_provider
      and u.auth_subject = p_auth_subject
    limit 1;
$function$;


revoke execute
on function public.find_app_user_by_identity(text, text)
from public;


grant execute
on function public.find_app_user_by_identity(text, text)
to careervoice_runtime;