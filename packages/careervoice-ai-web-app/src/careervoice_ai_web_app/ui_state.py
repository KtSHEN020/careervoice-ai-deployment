from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from copy import deepcopy

WORKSPACE_SESSION_ID_KEY = "workspace_session_id"
AUTHENTICATED_APP_USER_KEY = "authenticated_app_user"
AUTHENTICATION_SESSION_KEY = "authentication_session"

LOGIN_EMAIL_KEY = "login_email"
LOGIN_PENDING_EMAIL_KEY = "login_pending_email"
LOGIN_CODE_KEY = "login_code"
LOGIN_CODE_REQUESTED_KEY = "login_code_requested"
LOGIN_CODE_SENT_AT_KEY = "login_code_sent_at"

PROFILE_KEY = "career_profile"
PROFILE_EXTRACTOR_KEY = "profile_extractor"
PROFILE_CONFIRMED_KEY = "profile_confirmed"
PROFILE_REVISION_KEY = "profile_revision"

JOB_QUERIES_KEY = "job_queries"
JOB_SEARCH_SETTINGS_KEY = "job_search_settings"
COLLECTED_JOBS_KEY = "collected_jobs"
JOB_SEARCH_REVISION_KEY = "job_search_revision"

RECOMMENDATION_SETTINGS_KEY = "recommendation_settings"
RECOMMENDATIONS_KEY = "recommendations"


def clear_user_session_state(
    state: MutableMapping[str, object],
) -> None:
    """Remove all browser-session data when the current user signs out."""
    state.clear()


def clear_login_form_state(
    state: MutableMapping[str, object],
) -> None:
    """Remove temporary login-form values from browser state."""
    for key in (
        LOGIN_EMAIL_KEY,
        LOGIN_PENDING_EMAIL_KEY,
        LOGIN_CODE_KEY,
        LOGIN_CODE_REQUESTED_KEY,
        LOGIN_CODE_SENT_AT_KEY,
    ):
        state.pop(
            key,
            None,
        )


def _integer_state_value(
    state: Mapping[str, object],
    key: str,
) -> int:
    value = state.get(key, 0)

    if not isinstance(value, int):
        return 0

    return value


def _clear_recommendation_state(
    state: MutableMapping[str, object],
) -> None:
    state[RECOMMENDATION_SETTINGS_KEY] = None
    state[RECOMMENDATIONS_KEY] = None


def record_profile_extraction(
    state: MutableMapping[str, object],
    *,
    profile: Mapping[str, object],
    extractor: str,
) -> None:
    """Store a new profile and invalidate later workflow stages."""
    current_revision = _integer_state_value(
        state,
        PROFILE_REVISION_KEY,
    )

    state[PROFILE_KEY] = dict(profile)
    state[PROFILE_EXTRACTOR_KEY] = extractor
    state[PROFILE_CONFIRMED_KEY] = False
    state[JOB_QUERIES_KEY] = ()
    state[JOB_SEARCH_SETTINGS_KEY] = None
    state[COLLECTED_JOBS_KEY] = None
    state[JOB_SEARCH_REVISION_KEY] = 0
    _clear_recommendation_state(state)
    state[PROFILE_REVISION_KEY] = current_revision + 1


def record_profile_confirmation(
    state: MutableMapping[str, object],
    *,
    profile: Mapping[str, object],
    job_queries: Sequence[str],
) -> None:
    """Store the reviewed profile and confirmed search roles."""
    current_revision = _integer_state_value(
        state,
        PROFILE_REVISION_KEY,
    )

    state[PROFILE_KEY] = dict(profile)
    state[PROFILE_CONFIRMED_KEY] = True
    state[JOB_QUERIES_KEY] = tuple(job_queries)
    state[JOB_SEARCH_SETTINGS_KEY] = None
    state[COLLECTED_JOBS_KEY] = None
    state[JOB_SEARCH_REVISION_KEY] = 0
    _clear_recommendation_state(state)
    state[PROFILE_REVISION_KEY] = current_revision + 1


def record_job_search(
    state: MutableMapping[str, object],
    *,
    settings: Mapping[str, object],
    jobs: Sequence[Mapping[str, object]],
) -> None:
    """Store completed job-search settings and collected jobs."""
    current_revision = _integer_state_value(
        state,
        JOB_SEARCH_REVISION_KEY,
    )

    state[JOB_SEARCH_SETTINGS_KEY] = dict(settings)
    state[COLLECTED_JOBS_KEY] = [
        dict(job)
        for job in jobs
    ]
    _clear_recommendation_state(state)
    state[JOB_SEARCH_REVISION_KEY] = current_revision + 1


def record_recommendations(
    state: MutableMapping[str, object],
    *,
    settings: Mapping[str, object],
    document: Mapping[str, object],
) -> None:
    """Store completed ranking settings and recommendation output."""
    state[RECOMMENDATION_SETTINGS_KEY] = dict(settings)
    state[RECOMMENDATIONS_KEY] = deepcopy(dict(document))


def profile_widget_key(
    state: Mapping[str, object],
    field_name: str,
) -> str:
    """Return a profile widget key tied to the profile revision."""
    revision = _integer_state_value(
        state,
        PROFILE_REVISION_KEY,
    )

    return f"profile_{field_name}_{revision}"


def job_search_widget_key(
    state: Mapping[str, object],
    field_name: str,
) -> str:
    """Return a job-search widget key tied to the profile revision."""
    revision = _integer_state_value(
        state,
        PROFILE_REVISION_KEY,
    )

    return f"job_search_{field_name}_{revision}"


def recommendation_widget_key(
    state: Mapping[str, object],
    field_name: str,
) -> str:
    """Return a recommendation widget key tied to the job-search revision."""
    revision = _integer_state_value(
        state,
        JOB_SEARCH_REVISION_KEY,
    )

    return f"recommendation_{field_name}_{revision}"