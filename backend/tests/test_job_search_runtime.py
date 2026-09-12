from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from uuid import UUID

from careervoice_ai_orchestrator.models import (
    WorkflowConfig,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.job_search_runtime import (
    CareerVoiceJobSearchWorkflowFactory,
    build_job_search_service,
)
from backend.app.job_search_service import (
    JobSearchService,
)
from backend.app.job_search_usage import (
    PersistentJobSearchUsageRecorder,
)
from backend.app.main import create_runtime_app


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
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
                "id": "job-1",
                "title": (
                    "Junior Backend Developer"
                ),
                "company": "Example Company",
                "location": "Adelaide",
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


def database_environment() -> dict[str, str]:
    return {
        "DATABASE_HOST": (
            "example.pooler.supabase.com"
        ),
        "DATABASE_PORT": "5432",
        "DATABASE_NAME": "postgres",
        "DATABASE_USER": "runtime-user",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_SSLMODE": "require",
    }


def test_workflow_factory_builds_real_job_search_workflow(
    tmp_path: Path,
) -> None:
    gateway = FakeGateway()

    factory = CareerVoiceJobSearchWorkflowFactory(
        gateway_factory=lambda: gateway,
    )

    workflow = factory(
        user=create_user(),
        output_language="zh-CN",
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workflow.confirm_profile(
        profile=career_profile(),
        profile_edits={},
        workspace=workspace,
    )

    result = workflow.search_jobs(
        roles=[
            "backend developer",
        ],
        location="Adelaide",
        max_results_per_role=5,
        source="adzuna",
        workspace=workspace,
    )

    assert len(result.jobs) == 1

    assert (
        result.jobs[0]["title"]
        == "Junior Backend Developer"
    )

    assert (
        gateway.collect_config_seen
        is not None
    )

    config = gateway.collect_config_seen

    assert config.output_language == "zh-CN"
    assert config.job_source == "adzuna"
    assert config.job_queries == (
        "backend developer",
    )
    assert config.job_location == "Adelaide"
    assert config.job_max_results == 5

    workspace.clear()


def test_job_search_runtime_is_unconfigured_without_database() -> None:
    service = build_job_search_service(
        settings=BackendSettings(
            environment="test",
        ),
        environment={},
    )

    assert service is None


def test_job_search_runtime_builds_persistent_service() -> None:
    service = build_job_search_service(
        settings=BackendSettings(
            environment="test",
            daily_ai_unit_limit=60,
        ),
        environment=database_environment(),
    )

    assert isinstance(
        service,
        JobSearchService,
    )

    assert isinstance(
        service.workflow_factory,
        CareerVoiceJobSearchWorkflowFactory,
    )

    assert isinstance(
        service.usage_recorder,
        PersistentJobSearchUsageRecorder,
    )

    assert isinstance(
        service.usage_recorder.repository,
        PostgresPersistentUsageRepository,
    )

    assert (
        service.usage_recorder.daily_ai_unit_limit
        == 60
    )


def test_runtime_app_leaves_job_search_unconfigured_without_database() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )

    assert (
        app.state.job_search_provider
        is None
    )


def test_runtime_app_configures_job_search_with_database() -> None:
    environment = database_environment()

    environment.update(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
            "CAREERVOICE_DAILY_AI_UNIT_LIMIT": "60",
            "SUPABASE_URL": (
                "https://example.supabase.co"
            ),
            "SUPABASE_PUBLISHABLE_KEY": (
                "test-publishable-key"
            ),
        }
    )

    app = create_runtime_app(
        environment
    )

    provider = (
        app.state.job_search_provider
    )

    assert isinstance(
        provider,
        JobSearchService,
    )

    assert isinstance(
        provider.workflow_factory,
        CareerVoiceJobSearchWorkflowFactory,
    )

    assert isinstance(
        provider.usage_recorder,
        PersistentJobSearchUsageRecorder,
    )

    assert (
        provider.usage_recorder.daily_ai_unit_limit
        == 60
    )

    assert isinstance(
        provider.usage_recorder.repository,
        PostgresPersistentUsageRepository,
    )