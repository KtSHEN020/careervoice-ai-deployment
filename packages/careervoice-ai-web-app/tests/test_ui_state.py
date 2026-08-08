from __future__ import annotations

from careervoice_ai_web_app.ui_state import (
    COLLECTED_JOBS_KEY,
    JOB_QUERIES_KEY,
    JOB_SEARCH_REVISION_KEY,
    JOB_SEARCH_SETTINGS_KEY,
    PROFILE_CONFIRMED_KEY,
    PROFILE_EXTRACTOR_KEY,
    PROFILE_KEY,
    PROFILE_REVISION_KEY,
    RECOMMENDATION_SETTINGS_KEY,
    RECOMMENDATIONS_KEY,
    job_search_widget_key,
    profile_widget_key,
    recommendation_widget_key,
    record_job_search,
    record_profile_confirmation,
    record_profile_extraction,
    record_recommendations,
)


def test_record_profile_extraction_invalidates_later_stages() -> None:
    state: dict[str, object] = {
        PROFILE_CONFIRMED_KEY: True,
        JOB_QUERIES_KEY: ("old query",),
        JOB_SEARCH_SETTINGS_KEY: {"location": "Adelaide"},
        COLLECTED_JOBS_KEY: [{"title": "Old job"}],
        JOB_SEARCH_REVISION_KEY: 3,
        RECOMMENDATION_SETTINGS_KEY: {
            "scorer": "rules",
        },
        RECOMMENDATIONS_KEY: {
            "recommendations": [
                {
                    "job_id": "old-job",
                }
            ]
        },
        PROFILE_REVISION_KEY: 2,
    }

    record_profile_extraction(
        state,
        profile={
            "target_roles": ["software developer"],
        },
        extractor="rules",
    )

    assert state[PROFILE_KEY] == {
        "target_roles": ["software developer"],
    }
    assert state[PROFILE_EXTRACTOR_KEY] == "rules"
    assert state[PROFILE_CONFIRMED_KEY] is False
    assert state[JOB_QUERIES_KEY] == ()
    assert state[JOB_SEARCH_SETTINGS_KEY] is None
    assert state[COLLECTED_JOBS_KEY] is None
    assert state[JOB_SEARCH_REVISION_KEY] == 0
    assert state[RECOMMENDATION_SETTINGS_KEY] is None
    assert state[RECOMMENDATIONS_KEY] is None
    assert state[PROFILE_REVISION_KEY] == 3


def test_record_profile_confirmation_invalidates_old_jobs() -> None:
    state: dict[str, object] = {
        JOB_SEARCH_SETTINGS_KEY: {
            "location": "Old location",
        },
        COLLECTED_JOBS_KEY: [
            {
                "title": "Old job",
            }
        ],
        JOB_SEARCH_REVISION_KEY: 4,
        RECOMMENDATION_SETTINGS_KEY: {
            "scorer": "llm",
        },
        RECOMMENDATIONS_KEY: {
            "recommendations": [
                {
                    "job_id": "old-job",
                }
            ]
        },
        PROFILE_REVISION_KEY: 4,
    }

    record_profile_confirmation(
        state,
        profile={
            "target_roles": [
                "backend developer",
                "Python developer",
            ],
        },
        job_queries=(
            "backend developer",
            "Python developer",
        ),
    )

    assert state[PROFILE_CONFIRMED_KEY] is True
    assert state[JOB_QUERIES_KEY] == (
        "backend developer",
        "Python developer",
    )
    assert state[JOB_SEARCH_SETTINGS_KEY] is None
    assert state[COLLECTED_JOBS_KEY] is None
    assert state[JOB_SEARCH_REVISION_KEY] == 0
    assert state[RECOMMENDATION_SETTINGS_KEY] is None
    assert state[RECOMMENDATIONS_KEY] is None
    assert state[PROFILE_REVISION_KEY] == 5


def test_record_job_search_stores_settings_and_jobs() -> None:
    state: dict[str, object] = {
        JOB_SEARCH_REVISION_KEY: 2,
        RECOMMENDATION_SETTINGS_KEY: {
            "scorer": "rules",
        },
        RECOMMENDATIONS_KEY: {
            "recommendations": [
                {
                    "job_id": "old-job",
                }
            ]
        },
    }

    record_job_search(
        state,
        settings={
            "roles": ["software developer"],
            "location": "Adelaide",
            "max_results_per_role": 5,
            "source": "adzuna",
        },
        jobs=[
            {
                "job_id": "job-1",
                "title": "Junior Software Developer",
            }
        ],
    )

    assert state[JOB_SEARCH_SETTINGS_KEY] == {
        "roles": ["software developer"],
        "location": "Adelaide",
        "max_results_per_role": 5,
        "source": "adzuna",
    }
    assert state[COLLECTED_JOBS_KEY] == [
        {
            "job_id": "job-1",
            "title": "Junior Software Developer",
        }
    ]
    assert state[RECOMMENDATION_SETTINGS_KEY] is None
    assert state[RECOMMENDATIONS_KEY] is None
    assert state[JOB_SEARCH_REVISION_KEY] == 3


def test_record_recommendations_stores_settings_and_document() -> None:
    state: dict[str, object] = {}

    record_recommendations(
        state,
        settings={
            "scorer": "rules",
            "max_results": 5,
            "exclude_rejected": False,
        },
        document={
            "recommendations": [
                {
                    "job_id": "job-1",
                    "match_score": 84,
                }
            ],
            "total_jobs_scored": 1,
            "total_recommendations_returned": 1,
            "scoring_method": "rules",
        },
    )

    assert state[RECOMMENDATION_SETTINGS_KEY] == {
        "scorer": "rules",
        "max_results": 5,
        "exclude_rejected": False,
    }
    assert state[RECOMMENDATIONS_KEY] == {
        "recommendations": [
            {
                "job_id": "job-1",
                "match_score": 84,
            }
        ],
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
        "scoring_method": "rules",
    }


def test_profile_widget_key_changes_with_profile_revision() -> None:
    state: dict[str, object] = {
        PROFILE_REVISION_KEY: 4,
    }

    assert profile_widget_key(
        state,
        "skills",
    ) == "profile_skills_4"

    state[PROFILE_REVISION_KEY] = 5

    assert profile_widget_key(
        state,
        "skills",
    ) == "profile_skills_5"


def test_job_search_widget_key_uses_profile_revision() -> None:
    state: dict[str, object] = {
        PROFILE_REVISION_KEY: 7,
    }

    assert job_search_widget_key(
        state,
        "location",
    ) == "job_search_location_7"


def test_recommendation_widget_key_uses_job_search_revision() -> None:
    state: dict[str, object] = {
        JOB_SEARCH_REVISION_KEY: 6,
    }

    assert recommendation_widget_key(
        state,
        "scorer",
    ) == "recommendation_scorer_6"