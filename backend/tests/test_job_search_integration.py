from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from careervoice_ai_orchestrator.models import (
    WorkflowConfig,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.job_search_runtime import (
    CareerVoiceJobSearchWorkflowFactory,
)
from backend.app.job_search_service import (
    JobSearchService,
)
from backend.app.main import create_app
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


class FakeJobSearchUsageRecorder:
    def __init__(self) -> None:
        self.users_seen: list[AppUser] = []

    def record_job_search(
        self,
        *,
        user: AppUser,
    ) -> None:
        self.users_seen.append(
            user
        )


class FakeGateway:
    def __init__(self) -> None:
        self.collect_config_seen: (
            WorkflowConfig | None
        ) = None

    def save_career_profile(
        self,
        profile: Mapping[str, object],
        profile_path: str | Path,
    ) -> Path:
        del profile

        output_path = Path(
            profile_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            "{}",
            encoding="utf-8",
        )

        return output_path

    def resolve_queries(
        self,
        config: WorkflowConfig,
    ) -> tuple[str, ...]:
        del config

        return (
            "backend developer",
        )

    def collect_jobs(
        self,
        config: WorkflowConfig,
    ) -> list[dict[str, object]]:
        self.collect_config_seen = config

        return [
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
        ]

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        raise AssertionError(
            "Profile extraction should not run."
        )

    def generate_recommendations(
        self,
        config: WorkflowConfig,
    ) -> dict[str, object]:
        raise AssertionError(
            "Recommendation generation should not run."
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


def test_job_search_api_reaches_real_careervoice_workflow() -> None:
    user = create_user()
    gateway = FakeGateway()
    usage_recorder = FakeJobSearchUsageRecorder()

    workflow_factory = (
        CareerVoiceJobSearchWorkflowFactory(
            gateway_factory=lambda: gateway,
        )
    )

    job_search_service = JobSearchService(
        workflow_factory=workflow_factory,
        usage_recorder=usage_recorder,
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
        job_search_provider=(
            job_search_service
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
        json={
            "profile": career_profile(),
            "roles": [
                "backend developer",
                "python developer",
            ],
            "location": "Adelaide",
            "max_results_per_role": 5,
            "source": "adzuna",
            "output_language": "zh-CN",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["settings"] == {
        "roles": [
            "backend developer",
            "python developer",
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

    assert gateway.collect_config_seen is not None

    config = gateway.collect_config_seen

    assert config.job_queries == (
        "backend developer",
        "python developer",
    )

    assert config.job_location == "Adelaide"
    assert config.job_max_results == 5
    assert config.job_source == "adzuna"
    assert config.output_language == "zh-CN"

    assert usage_recorder.users_seen == [
        user
    ]