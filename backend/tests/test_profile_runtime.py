from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import UUID

from careervoice_ai_orchestrator.models import (
    WorkflowConfig,
)
from careervoice_ai_web_app.persistent_usage import (
    DailyUsageSnapshot,
    UsageDecision,
    UsageOperation,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)
from careervoice_ai_web_app.session_workspace import (
    SessionWorkspace,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.config import BackendSettings
from backend.app.profile_runtime import (
    CareerVoiceProfileWorkflowFactory,
    build_profile_extraction_service,
)
from backend.app.profile_service import (
    ProfileExtractionService,
)
from backend.app.main import create_runtime_app


TEST_USER_ID = UUID(
    "11111111-2222-3333-4444-555555555555"
)


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


class FakeGateway:
    def __init__(self) -> None:
        self.config_seen: WorkflowConfig | None = None
        self.text_seen: str | None = None

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        self.config_seen = config
        self.text_seen = profile_input_text

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


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


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


def test_workflow_factory_uses_configured_ai_limit(
    tmp_path: Path,
) -> None:
    user = create_user()
    usage_repository = FakeUsageRepository()
    gateway = FakeGateway()

    factory = CareerVoiceProfileWorkflowFactory(
        usage_repository=usage_repository,
        daily_ai_unit_limit=60,
        gateway_factory=lambda: gateway,
    )

    workflow = factory(
        user=user,
        output_language="zh-CN",
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workflow.extract_text_profile(
        career_preference_text=(
            "I want a backend development role."
        ),
        extractor="llm",
        workspace=workspace,
    )

    assert len(
        usage_repository.consume_calls
    ) == 1

    usage_call = (
        usage_repository.consume_calls[0]
    )

    assert usage_call["user"] is user
    assert usage_call["units"] == 1
    assert usage_call["daily_limit"] == 60
    assert (
        usage_call["operation"]
        == UsageOperation.PROFILE_EXTRACTION
    )

    assert gateway.text_seen == (
        "I want a backend development role."
    )

    assert gateway.config_seen is not None
    assert (
        gateway.config_seen.output_language
        == "zh-CN"
    )
    assert (
        gateway.config_seen.profile_extractor
        == "llm"
    )

    workspace.clear()


def test_rules_profile_does_not_consume_ai_units(
    tmp_path: Path,
) -> None:
    usage_repository = FakeUsageRepository()
    gateway = FakeGateway()

    factory = CareerVoiceProfileWorkflowFactory(
        usage_repository=usage_repository,
        daily_ai_unit_limit=60,
        gateway_factory=lambda: gateway,
    )

    workflow = factory(
        user=create_user(),
        output_language="en",
    )

    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workflow.extract_text_profile(
        career_preference_text=(
            "I want a software development role."
        ),
        extractor="rules",
        workspace=workspace,
    )

    assert usage_repository.consume_calls == []

    workspace.clear()


def test_profile_runtime_is_unconfigured_without_database() -> None:
    service = build_profile_extraction_service(
        settings=BackendSettings(
            environment="test",
        ),
        environment={},
    )

    assert service is None


def test_profile_runtime_builds_persistent_service() -> None:
    service = build_profile_extraction_service(
        settings=BackendSettings(
            environment="test",
            daily_ai_unit_limit=60,
        ),
        environment=database_environment(),
    )

    assert isinstance(
        service,
        ProfileExtractionService,
    )

    workflow_factory = (
        service.workflow_factory
    )

    assert isinstance(
        workflow_factory,
        CareerVoiceProfileWorkflowFactory,
    )

    assert isinstance(
        workflow_factory.usage_repository,
        PostgresPersistentUsageRepository,
    )

    assert (
        workflow_factory.daily_ai_unit_limit
        == 60
    )


def test_runtime_app_leaves_profile_service_unconfigured_without_database() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )

    assert (
        app.state.profile_extraction_provider
        is None
    )


def test_runtime_app_configures_profile_service_with_database() -> None:
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
        app.state.profile_extraction_provider
    )

    assert isinstance(
        provider,
        ProfileExtractionService,
    )

    workflow_factory = (
        provider.workflow_factory
    )

    assert isinstance(
        workflow_factory,
        CareerVoiceProfileWorkflowFactory,
    )

    assert (
        workflow_factory.daily_ai_unit_limit
        == 60
    )

    assert isinstance(
        workflow_factory.usage_repository,
        PostgresPersistentUsageRepository,
    )