from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.public_limits import (
    MAX_RECOMMENDATIONS,
)
from careervoice_ai_web_app.recommendation_models import (
    RecommendationDocument,
    RecommendationSettings,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.main import create_app
from backend.app.recommendation_service import (
    RecommendationExecution,
)
from backend.app.security import (
    InvalidAccessTokenError,
)


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


@dataclass
class FakeCurrentUserResolver:
    user: AppUser

    def resolve(
        self,
        access_token: str,
    ) -> AppUser:
        if access_token != "valid-test-token":
            raise InvalidAccessTokenError(
                "Access token is invalid."
            )

        return self.user


class FakeRecommendationProvider:
    def __init__(
        self,
        *,
        quota_exhausted: bool = False,
    ) -> None:
        self.quota_exhausted = quota_exhausted

        self.calls: list[
            dict[str, object]
        ] = []

    def recommend(
        self,
        *,
        user: AppUser,
        profile: dict[str, object],
        jobs: list[dict[str, object]],
        scorer: object,
        max_results: object,
        exclude_rejected: object,
        output_language: str,
    ) -> RecommendationExecution:
        self.calls.append(
            {
                "user": user,
                "profile": profile,
                "jobs": jobs,
                "scorer": scorer,
                "max_results": max_results,
                "exclude_rejected": (
                    exclude_rejected
                ),
                "output_language": (
                    output_language
                ),
            }
        )

        if self.quota_exhausted:
            raise AIUsageLimitError(
                "No allowance remains."
            )

        settings = RecommendationSettings.from_values(
            scorer=scorer,
            max_results=max_results,
            exclude_rejected=exclude_rejected,
        )

        return RecommendationExecution(
            settings=settings,
            document=(
                RecommendationDocument.from_mapping(
                    {
                        "recommendations": [
                            {
                                "job_id": "adzuna-1",
                                "title": (
                                    "Junior Backend Developer"
                                ),
                                "company": (
                                    "Example Company"
                                ),
                                "match_score": 88,
                                "recommendation_level": (
                                    "strong_match"
                                ),
                                "reasons": [
                                    (
                                        "Strong Python "
                                        "alignment."
                                    ),
                                ],
                                "missing_skills": [
                                    "Docker",
                                ],
                                "penalties": [
                                    (
                                        "Conflicts with "
                                        "avoid sales roles."
                                    ),
                                ],
                                "uncertainties": [
                                    (
                                        "Cloud experience "
                                        "is unclear."
                                    ),
                                ],
                                "is_rejected_by_constraints": (
                                    True
                                ),
                                "scoring_method": (
                                    settings.scorer
                                ),
                                "score_breakdown": {
                                    "final_score": 88,
                                },
                                "matched_details": {
                                    "matched_skills": [
                                        "Python",
                                    ],
                                    "matched_hard_constraints": [
                                        "avoid sales roles",
                                    ],
                                },
                            }
                        ],
                        "total_jobs_scored": 1,
                        "total_jobs_scored_with_llm": (
                            1
                            if settings.scorer == "llm"
                            else 0
                        ),
                        "llm_candidate_limit": (
                            10
                            if settings.scorer == "llm"
                            else None
                        ),
                        "total_recommendations_returned": 1,
                        "scoring_method": (
                            settings.scorer
                        ),
                    }
                )
            ),
            output_language=output_language,
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
        ],
        "experience_level": "junior",
        "preferred_locations": [
            "Adelaide",
        ],
        "preferred_work_types": [
            "hybrid",
        ],
        "liked_areas": [],
        "disliked_areas": [],
        "hard_constraints": [
            "avoid sales roles",
        ],
        "career_goals": [],
        "notes": [],
    }


def normalized_job() -> dict[str, object]:
    return {
        "job_id": "adzuna-1",
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
        ],
        "preferred_skills": [],
        "responsibilities": [
            "Build backend services.",
        ],
        "tags": [
            "backend",
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


def valid_payload() -> dict[str, object]:
    return {
        "profile": career_profile(),
        "jobs": [
            normalized_job(),
        ],
        "scorer": "llm",
        "max_results": 5,
        "exclude_rejected": False,
        "output_language": "en",
    }


def create_test_client(
    provider: FakeRecommendationProvider | None,
) -> TestClient:
    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=create_user()
            )
        ),
        recommendation_provider=provider,
    )

    return TestClient(app)


def test_recommendations_require_authentication() -> None:
    provider = FakeRecommendationProvider()

    client = create_test_client(
        provider
    )

    response = client.post(
        "/api/v1/recommendations",
        json=valid_payload(),
    )

    assert response.status_code == 401
    assert provider.calls == []


def test_recommendations_return_structured_results() -> None:
    provider = FakeRecommendationProvider()

    client = create_test_client(
        provider
    )

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json={
            **valid_payload(),
            "output_language": "zh-CN",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["settings"] == {
        "scorer": "llm",
        "max_results": 5,
        "exclude_rejected": False,
    }

    assert body["scoring_method"] == "llm"
    assert body["output_language"] == "zh-CN"

    assert body["total_jobs_scored"] == 1
    assert body["total_jobs_scored_with_llm"] == 1
    assert body["llm_candidate_limit"] == 10

    assert (
        body["total_recommendations_returned"]
        == 1
    )

    recommendation = (
        body["recommendations"][0]
    )

    assert recommendation["match_score"] == 88

    assert recommendation["missing_skills"] == [
        "Docker"
    ]

    assert recommendation["uncertainties"] == [
        "Cloud experience is unclear."
    ]

    assert (
        recommendation[
            "is_rejected_by_constraints"
        ]
        is True
    )

    assert (
        recommendation[
            "matched_details"
        ]["matched_hard_constraints"]
        == [
            "avoid sales roles",
        ]
    )

    assert len(provider.calls) == 1
    assert provider.calls[0]["user"].email == (
        "tester@example.com"
    )

    assert (
        provider.calls[0]["output_language"]
        == "zh-CN"
    )


def test_recommendations_enforce_public_result_limit() -> None:
    provider = FakeRecommendationProvider()

    client = create_test_client(
        provider
    )

    payload = valid_payload()

    payload["max_results"] = (
        MAX_RECOMMENDATIONS + 1
    )

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=payload,
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_recommendations_require_at_least_one_job() -> None:
    provider = FakeRecommendationProvider()

    client = create_test_client(
        provider
    )

    payload = valid_payload()
    payload["jobs"] = []

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=payload,
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_recommendations_return_429_when_ai_quota_is_exhausted() -> None:
    provider = FakeRecommendationProvider(
        quota_exhausted=True
    )

    client = create_test_client(
        provider
    )

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=valid_payload(),
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": (
            "Daily AI allowance is insufficient "
            "for this request."
        )
    }


def test_recommendations_fail_closed_when_service_is_unconfigured() -> None:
    client = create_test_client(
        None
    )

    response = client.post(
        "/api/v1/recommendations",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=valid_payload(),
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "Recommendation service is unavailable."
        )
    }