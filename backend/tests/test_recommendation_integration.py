from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.main import create_app
from backend.app.recommendation_runtime import (
    CareerVoiceRecommendationWorkflowFactory,
)
from backend.app.recommendation_service import (
    RecommendationService,
)
from backend.app.security import (
    InvalidAccessTokenError,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


class FakeCurrentUserResolver:
    def __init__(
        self,
        user: AppUser,
    ) -> None:
        self.user = user

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        if access_token != "valid-test-token":
            raise InvalidAccessTokenError(
                "Access token is invalid."
            )

        return self.user


class FakeUsageRepository:
    def __init__(self) -> None:
        self.consume_calls: list[
            dict[str, object]
        ] = []

    def get_daily_usage(
        self,
        *,
        user: AppUser,
        usage_date: date,
    ) -> DailyUsageSnapshot:
        return DailyUsageSnapshot(
            user_id=user.id,
            usage_date=usage_date,
            ai_units_used=0,
            ai_profile_extractions=0,
            voice_transcriptions=0,
            document_recognitions=0,
            ai_ranking_runs=0,
            job_searches=0,
        )

    def consume(
        self,
        *,
        user: AppUser,
        usage_date: date,
        units: int,
        daily_limit: int,
        operation: UsageOperation,
    ) -> UsageDecision:
        self.consume_calls.append(
            {
                "user": user,
                "usage_date": usage_date,
                "units": units,
                "daily_limit": daily_limit,
                "operation": operation,
            }
        )

        return UsageDecision(
            allowed=True,
            ai_units_used=units,
            remaining_ai_units=(
                daily_limit - units
            ),
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def career_profile() -> dict[str, object]:
    return {
        "target_roles": [
            "backend developer",
        ],
        "skills": [
            "Python",
            "Git",
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Adelaide",
        ],
        "preferred_work_types": [
            "hybrid",
        ],
        "liked_areas": [
            "backend development",
        ],
        "disliked_areas": [],
        "hard_constraints": [],
        "career_goals": [
            "software engineering",
        ],
        "notes": [],
    }


def normalized_job() -> dict[str, object]:
    return {
        "job_id": "job-1",
        "title": "Junior Backend Developer",
        "company": "Example Company",
        "location": "Adelaide",
        "work_type": "hybrid",
        "seniority": "junior",
        "description": (
            "Build Python backend services."
        ),
        "required_skills": [
            "Python",
            "Git",
        ],
        "preferred_skills": [
            "Docker",
        ],
        "responsibilities": [
            "Build backend services.",
        ],
        "tags": [
            "backend development",
            "software engineering",
        ],
        "source": "adzuna",
        "source_url": (
            "https://example.com/job/1"
        ),
        "collected_at": datetime(
            2026,
            9,
            12,
            6,
            0,
            tzinfo=UTC,
        ).isoformat(),
    }


def test_recommendation_api_reaches_real_rule_based_recommender() -> None:
    user = create_user()
    usage_repository = FakeUsageRepository()

    workflow_factory = (
        CareerVoiceRecommendationWorkflowFactory(
            usage_repository=usage_repository,
            daily_ai_unit_limit=40,
        )
    )

    recommendation_service = RecommendationService(
        workflow_factory=workflow_factory
    )

    app = create_app(
        settings=BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        recommendation_provider=(
            recommendation_service
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            "profile": career_profile(),
            "jobs": [
                normalized_job(),
            ],
            "scorer": "rules",
            "max_results": 5,
            "exclude_rejected": False,
            "output_language": "en",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["settings"] == {
        "scorer": "rules",
        "max_results": 5,
        "exclude_rejected": False,
    }

    assert body["scoring_method"] == "rules"
    assert body["output_language"] == "en"

    assert body["total_jobs_scored"] == 1
    assert (
        body["total_recommendations_returned"]
        == 1
    )

    assert len(
        body["recommendations"]
    ) == 1

    recommendation = (
        body["recommendations"][0]
    )

    assert recommendation["job_id"] == "job-1"

    assert (
        recommendation["title"]
        == "Junior Backend Developer"
    )

    assert (
        recommendation["scoring_method"]
        == "rules"
    )

    assert isinstance(
        recommendation["match_score"],
        int,
    )

    assert (
        recommendation[
            "is_rejected_by_constraints"
        ]
        is False
    )

    assert isinstance(
        recommendation["reasons"],
        list,
    )

    assert isinstance(
        recommendation["missing_skills"],
        list,
    )

    assert isinstance(
        recommendation["penalties"],
        list,
    )

    assert isinstance(
        recommendation["matched_details"],
        dict,
    )

    assert (
        usage_repository.consume_calls
        == []
    )