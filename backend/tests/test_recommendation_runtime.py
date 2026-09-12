from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from uuid import UUID

from careervoice_ai_orchestrator.models import (
    WorkflowConfig,
)
from careervoice_ai_web_app.ai_usage import (
    AI_RANKING_AI_UNITS,
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
from backend.app.recommendation_runtime import (
    CareerVoiceRecommendationWorkflowFactory,
    build_recommendation_service,
)
from backend.app.recommendation_service import (
    RecommendationService,
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

    def generate_recommendations(
        self,
        config: WorkflowConfig,
    ) -> dict[str, object]:
        self.config_seen = config

        return {
            "recommendations": [
                {
                    "job_id": "job-1",
                    "title": "Backend Developer",
                    "company": "Example Company",
                    "match_score": 90,
                    "recommendation_level": (
                        "strong_match"
                    ),
                    "reasons": [
                        "Strong Python alignment.",
                    ],
                    "missing_skills": [],
                    "penalties": [],
                    "uncertainties": [],
                    "is_rejected_by_constraints": (
                        False
                    ),
                    "scoring_method": (
                        config.recommender_scorer
                    ),
                    "score_breakdown": {},
                    "matched_details": {},
                }
            ],
            "total_jobs_scored": 1,
            "total_recommendations_returned": 1,
            "scoring_method": (
                config.recommender_scorer
            ),
        }

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        raise AssertionError(
            "Profile extraction should not run."
        )

    def resolve_queries(
        self,
        config: WorkflowConfig,
    ) -> tuple[str, ...]:
        raise AssertionError(
            "Query resolution should not run."
        )

    def collect_jobs(
        self,
        config: WorkflowConfig,
    ) -> list[dict[str, object]]:
        raise AssertionError(
            "Job collection should not run."
        )


def create_user() -> AppUser:
    return AppUser(
        id=TEST_USER_ID,
        email="tester@example.com",
        auth_provider="supabase",
        auth_subject="provider-user-123",
        enabled=True,
    )


def create_workspace(
    tmp_path: Path,
) -> SessionWorkspace:
    workspace = SessionWorkspace.create(
        root_dir=tmp_path,
    )

    workspace.ensure_exists()

    workspace.profile_path.write_text(
        "{}",
        encoding="utf-8",
    )

    workspace.jobs_output_path.write_text(
        json.dumps(
            [
                {
                    "job_id": "job-1",
                    "title": "Backend Developer",
                    "company": "Example Company",
                    "location": "Adelaide",
                    "description": (
                        "Build backend services."
                    ),
                }
            ]
        ),
        encoding="utf-8",
    )

    return workspace


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


def test_rules_ranking_does_not_consume_ai_units(
    tmp_path: Path,
) -> None:
    usage_repository = FakeUsageRepository()
    gateway = FakeGateway()

    factory = (
        CareerVoiceRecommendationWorkflowFactory(
            usage_repository=usage_repository,
            daily_ai_unit_limit=60,
            gateway_factory=lambda: gateway,
        )
    )

    workflow = factory(
        user=create_user(),
        output_language="en",
    )

    workspace = create_workspace(
        tmp_path
    )

    result = workflow.rank_jobs(
        scorer="rules",
        max_results=5,
        exclude_rejected=False,
        workspace=workspace,
    )

    assert (
        usage_repository.consume_calls
        == []
    )

    assert result.settings.scorer == "rules"

    assert gateway.config_seen is not None
    assert (
        gateway.config_seen.recommender_scorer
        == "rules"
    )

    workspace.clear()


def test_llm_ranking_consumes_ten_ai_units_using_configured_limit(
    tmp_path: Path,
) -> None:
    user = create_user()
    usage_repository = FakeUsageRepository()
    gateway = FakeGateway()

    factory = (
        CareerVoiceRecommendationWorkflowFactory(
            usage_repository=usage_repository,
            daily_ai_unit_limit=60,
            gateway_factory=lambda: gateway,
        )
    )

    workflow = factory(
        user=user,
        output_language="zh-CN",
    )

    workspace = create_workspace(
        tmp_path
    )

    result = workflow.rank_jobs(
        scorer="llm",
        max_results=5,
        exclude_rejected=True,
        workspace=workspace,
    )

    assert len(
        usage_repository.consume_calls
    ) == 1

    usage_call = (
        usage_repository.consume_calls[0]
    )

    assert usage_call["user"] is user

    assert (
        usage_call["units"]
        == AI_RANKING_AI_UNITS
    )

    assert AI_RANKING_AI_UNITS == 10

    assert (
        usage_call["daily_limit"]
        == 60
    )

    assert (
        usage_call["operation"]
        == UsageOperation.AI_RANKING
    )

    assert result.settings.scorer == "llm"

    assert gateway.config_seen is not None

    assert (
        gateway.config_seen.recommender_scorer
        == "llm"
    )

    assert (
        gateway.config_seen.output_language
        == "zh-CN"
    )

    assert (
        gateway.config_seen.recommendation_max_results
        == 5
    )

    assert (
        gateway.config_seen.exclude_rejected
        is True
    )

    workspace.clear()


def test_recommendation_runtime_is_unconfigured_without_database() -> None:
    service = build_recommendation_service(
        settings=BackendSettings(
            environment="test",
        ),
        environment={},
    )

    assert service is None


def test_recommendation_runtime_builds_persistent_service() -> None:
    service = build_recommendation_service(
        settings=BackendSettings(
            environment="test",
            daily_ai_unit_limit=60,
        ),
        environment=database_environment(),
    )

    assert isinstance(
        service,
        RecommendationService,
    )

    factory = service.workflow_factory

    assert isinstance(
        factory,
        CareerVoiceRecommendationWorkflowFactory,
    )

    assert isinstance(
        factory.usage_repository,
        PostgresPersistentUsageRepository,
    )

    assert (
        factory.daily_ai_unit_limit
        == 60
    )


def test_runtime_app_leaves_recommendation_service_unconfigured_without_database() -> None:
    app = create_runtime_app(
        {
            "CAREERVOICE_ENVIRONMENT": "test",
        }
    )

    assert (
        app.state.recommendation_provider
        is None
    )


def test_runtime_app_configures_recommendation_service_with_database() -> None:
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
        app.state.recommendation_provider
    )

    assert isinstance(
        provider,
        RecommendationService,
    )

    factory = provider.workflow_factory

    assert isinstance(
        factory,
        CareerVoiceRecommendationWorkflowFactory,
    )

    assert (
        factory.daily_ai_unit_limit
        == 60
    )

    assert isinstance(
        factory.usage_repository,
        PostgresPersistentUsageRepository,
    )