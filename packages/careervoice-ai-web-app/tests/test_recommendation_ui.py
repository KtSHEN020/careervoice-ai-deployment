from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from streamlit.testing.v1 import AppTest

from careervoice_ai_web_app.ai_usage import (
    AIUsageStatus,
)
from careervoice_ai_web_app.authentication import (
    AuthenticationSession,
)
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.public_limits import (
    MAX_RECOMMENDATIONS,
)
from careervoice_ai_web_app.ui_state import (
    AUTHENTICATED_APP_USER_KEY,
    AUTHENTICATION_SESSION_KEY,
    COLLECTED_JOBS_KEY,
    JOB_QUERIES_KEY,
    JOB_SEARCH_REVISION_KEY,
    PROFILE_CONFIRMED_KEY,
    PROFILE_KEY,
    PROFILE_REVISION_KEY,
    RECOMMENDATION_SETTINGS_KEY,
    RECOMMENDATIONS_KEY,
)
from careervoice_ai_web_app.user_models import (
    AppUser,
    AuthenticatedIdentity,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"


@pytest.fixture(autouse=True)
def _configure_auth_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provide non-secret authentication configuration for UI tests."""
    monkeypatch.setenv(
        "SUPABASE_URL",
        "https://example.supabase.co",
    )
    monkeypatch.setenv(
        "SUPABASE_PUBLISHABLE_KEY",
        "test-publishable-key",
    )
    monkeypatch.setenv(
        "DATABASE_HOST",
        "example.pooler.supabase.com",
    )
    monkeypatch.setenv(
        "DATABASE_PORT",
        "5432",
    )
    monkeypatch.setenv(
        "DATABASE_NAME",
        "postgres",
    )
    monkeypatch.setenv(
        "DATABASE_USER",
        "postgres.example",
    )
    monkeypatch.setenv(
        "DATABASE_PASSWORD",
        "test-password",
    )
    monkeypatch.setenv(
        "DATABASE_SSLMODE",
        "require",
    )
    monkeypatch.setattr(
        PersistentAIUsageBudget,
        "status",
        lambda self: AIUsageStatus(
            limit=20,
            used=7,
            remaining=13,
            profile_extractions=2,
            voice_transcriptions=1,
            document_recognitions=0,
            ai_ranking_runs=0,
        ),
    )


def _seed_completed_job_search(
    app: AppTest,
) -> None:
    identity = AuthenticatedIdentity(
        provider="supabase",
        subject="auth-user-123",
        email="tester@example.com",
    )

    app.session_state[
        AUTHENTICATION_SESSION_KEY
    ] = AuthenticationSession(
        identity=identity,
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=1_800_000_000,
    )

    app.session_state[
        AUTHENTICATED_APP_USER_KEY
    ] = AppUser(
        id=UUID(
            "12345678-1234-5678-1234-567812345678"
        ),
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="auth-user-123",
        enabled=True,
    )

    app.session_state[PROFILE_KEY] = {
        "target_roles": [
            "software developer",
        ],
        "preferred_locations": [
            "Adelaide",
        ],
    }

    app.session_state[PROFILE_CONFIRMED_KEY] = True

    app.session_state[JOB_QUERIES_KEY] = (
        "software developer",
    )

    app.session_state[PROFILE_REVISION_KEY] = 2
    app.session_state[JOB_SEARCH_REVISION_KEY] = 1

    app.session_state[COLLECTED_JOBS_KEY] = [
        {
            "job_id": "job-1",
            "title": "Junior Software Developer",
        },
        {
            "job_id": "job-2",
            "title": "Backend Developer",
        },
    ]


def test_app_renders_recommendation_form_after_job_search() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    _seed_completed_job_search(app)

    app.run(timeout=15)

    assert len(app.exception) == 0

    assert any(
        subheader.value
        == "Rank and explain your job matches"
        for subheader in app.subheader
    )

    assert any(
        selectbox.label == "Ranking method"
        for selectbox in app.selectbox
    )

    assert any(
        number_input.label
        == "Maximum recommendations"
        for number_input in app.number_input
    )

    assert any(
        checkbox.label
        == (
            "Hide jobs that conflict with "
            "non-negotiable requirements"
        )
        for checkbox in app.checkbox
    )

    assert any(
        button.label == "Generate recommendations"
        for button in app.button
    )


def test_app_renders_readable_recommendation_cards() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    _seed_completed_job_search(app)

    app.session_state[RECOMMENDATION_SETTINGS_KEY] = {
        "scorer": "rules",
        "max_results": 1,
        "exclude_rejected": False,
    }

    app.session_state[RECOMMENDATIONS_KEY] = {
        "recommendations": [
            {
                "job_id": "job-1",
                "title": "Junior Software Developer",
                "company": "Example Company",
                "match_score": 84,
                "recommendation_level": "strong_match",
                "reasons": [
                    "Matches the preferred role.",
                ],
                "missing_skills": [
                    "Docker",
                ],
                "penalties": [],
                "uncertainties": [],
                "is_rejected_by_constraints": False,
                "scoring_method": "rules",
                "score_breakdown": {
                    "skill_match": 30,
                },
                "matched_details": {
                    "matched_skills": [
                        "Python",
                    ],
                },
            }
        ],
        "total_jobs_scored": 2,
        "total_recommendations_returned": 1,
        "scoring_method": "rules",
    }

    app.run(timeout=15)

    assert len(app.exception) == 0

    assert any(
        subheader.value == "Recommended jobs"
        for subheader in app.subheader
    )

    assert any(
        "Junior Software Developer"
        in markdown.value
        for markdown in app.markdown
    )

    assert any(
        metric.label == "Match score"
        and metric.value == "84/100"
        for metric in app.metric
    )

    assert any(
        download_button.label
        == "Download recommendations"
        for download_button in app.download_button
    )

    assert any(
        metric.label == "Ranking method"
        and metric.value == "Standard"
        for metric in app.metric
    )


def test_app_marks_constraint_rejected_recommendation() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    _seed_completed_job_search(app)

    app.session_state[RECOMMENDATIONS_KEY] = {
        "recommendations": [
            {
                "job_id": "job-2",
                "title": "Principal Software Developer",
                "company": "Example Company",
                "match_score": 35,
                "recommendation_level": "weak_match",
                "reasons": [],
                "missing_skills": [],
                "penalties": [
                    "The role appears more senior than preferred.",
                ],
                "uncertainties": [],
                "is_rejected_by_constraints": True,
                "scoring_method": "rules",
            }
        ],
        "total_jobs_scored": 2,
        "total_recommendations_returned": 1,
        "scoring_method": "rules",
    }

    app.run(timeout=15)

    assert len(app.exception) == 0

    assert any(
        "non-negotiable requirements" in error.value
        for error in app.error
    )

def test_app_displays_ai_assisted_ranking_label() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    _seed_completed_job_search(app)

    app.session_state[RECOMMENDATION_SETTINGS_KEY] = {
        "scorer": "llm",
        "max_results": 1,
        "exclude_rejected": False,
    }

    app.session_state[RECOMMENDATIONS_KEY] = {
        "recommendations": [
            {
                "job_id": "job-1",
                "title": "Backend Developer",
                "company": "Example Company",
                "match_score": 82,
                "recommendation_level": "strong_match",
                "reasons": [],
                "missing_skills": [],
                "penalties": [],
                "uncertainties": [],
                "is_rejected_by_constraints": False,
                "scoring_method": "llm",
            }
        ],
        "total_jobs_scored": 1,
        "total_recommendations_returned": 1,
        "scoring_method": "llm",
    }

    app.run(timeout=15)

    assert len(app.exception) == 0

    assert any(
        metric.label == "Ranking method"
        and metric.value == "AI-assisted"
        for metric in app.metric
    )


def test_recommendation_form_caps_public_maximum() -> None:
    app = AppTest.from_file(
        str(APP_PATH)
    )

    _seed_completed_job_search(app)

    app.session_state[COLLECTED_JOBS_KEY] = [
        {
            "job_id": f"job-{index}",
            "title": f"Developer {index}",
        }
        for index in range(
            MAX_RECOMMENDATIONS + 2
        )
    ]

    app.run(timeout=15)

    assert len(app.exception) == 0

    max_results_input = next(
        number_input
        for number_input in app.number_input
        if number_input.label
        == "Maximum recommendations"
    )

    assert (
        max_results_input.max
        == MAX_RECOMMENDATIONS
    )