from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_web_app.models import (
    JobSearchSettings,
)
from careervoice_ai_web_app.public_limits import (
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.job_search_service import (
    JobSearchExecution,
)
from backend.app.main import create_app
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


class FakeJobSearchProvider:
    def __init__(
        self,
        *,
        should_fail_validation: bool = False,
    ) -> None:
        self.should_fail_validation = (
            should_fail_validation
        )

        self.calls: list[
            dict[str, object]
        ] = []

    def search(
        self,
        *,
        user: AppUser,
        profile: dict[str, object],
        roles: list[str],
        location: object,
        max_results_per_role: object,
        source: str,
        output_language: str,
    ) -> JobSearchExecution:
        self.calls.append(
            {
                "user": user,
                "profile": profile,
                "roles": roles,
                "location": location,
                "max_results_per_role": (
                    max_results_per_role
                ),
                "source": source,
                "output_language": (
                    output_language
                ),
            }
        )

        if self.should_fail_validation:
            raise ValueError(
                "Invalid job-search settings."
            )

        return JobSearchExecution(
            settings=JobSearchSettings.from_values(
                roles=roles,
                location=location,
                max_results_per_role=(
                    max_results_per_role
                ),
                source=source,
            ),
            jobs=[
                {
                    "job_id": "adzuna-1",
                    "title": (
                        "Junior Backend Developer"
                    ),
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
                    ),
                }
            ],
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
        "hard_constraints": [],
        "career_goals": [],
        "notes": [],
    }


def valid_payload() -> dict[str, object]:
    return {
        "profile": career_profile(),
        "roles": [
            "backend developer",
        ],
        "location": "Adelaide",
        "max_results_per_role": 5,
        "source": "adzuna",
        "output_language": "en",
    }


def test_job_search_requires_authentication() -> None:
    user = create_user()
    provider = FakeJobSearchProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        job_search_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs/search",
        json=valid_payload(),
    )

    assert response.status_code == 401
    assert provider.calls == []


def test_job_search_returns_normalized_jobs() -> None:
    user = create_user()
    provider = FakeJobSearchProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=user
            )
        ),
        job_search_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs/search",
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
        "roles": [
            "backend developer",
        ],
        "location": "Adelaide",
        "max_results_per_role": 5,
        "source": "adzuna",
    }

    assert body["output_language"] == "zh-CN"

    assert len(body["jobs"]) == 1

    assert (
        body["jobs"][0]["job_id"]
        == "adzuna-1"
    )

    assert (
        body["jobs"][0]["title"]
        == "Junior Backend Developer"
    )

    assert provider.calls[0]["user"] is user

    assert provider.calls[0]["profile"] == (
        career_profile()
    )

    assert (
        provider.calls[0]["output_language"]
        == "zh-CN"
    )


def test_job_search_rejects_too_many_roles() -> None:
    provider = FakeJobSearchProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=create_user()
            )
        ),
        job_search_provider=provider,
    )

    client = TestClient(app)

    payload = valid_payload()

    payload["roles"] = [
        f"role-{index}"
        for index in range(
            MAX_JOB_QUERIES + 1
        )
    ]

    response = client.post(
        "/api/v1/jobs/search",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=payload,
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_job_search_rejects_too_many_results_per_role() -> None:
    provider = FakeJobSearchProvider()

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=create_user()
            )
        ),
        job_search_provider=provider,
    )

    client = TestClient(app)

    payload = valid_payload()

    payload["max_results_per_role"] = (
        MAX_JOB_RESULTS_PER_QUERY + 1
    )

    response = client.post(
        "/api/v1/jobs/search",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=payload,
    )

    assert response.status_code == 422
    assert provider.calls == []


def test_job_search_translates_domain_validation_error() -> None:
    provider = FakeJobSearchProvider(
        should_fail_validation=True
    )

    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=create_user()
            )
        ),
        job_search_provider=provider,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs/search",
        headers={
            "Authorization": (
                "Bearer valid-test-token"
            ),
        },
        json=valid_payload(),
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid job-search settings."
    }


def test_job_search_fails_closed_when_service_is_unconfigured() -> None:
    app = create_app(
        BackendSettings(
            environment="test",
        ),
        current_user_resolver=(
            FakeCurrentUserResolver(
                user=create_user()
            )
        ),
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/jobs/search",
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
            "Job search service is unavailable."
        )
    }