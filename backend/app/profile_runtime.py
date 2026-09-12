"""Runtime construction for CareerVoice profile extraction."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from careervoice_ai_web_app.orchestrator_gateway import (
    Repo4OrchestratorGateway,
    SupportsOrchestratorGateway,
)
from careervoice_ai_web_app.persistent_ai_usage import (
    PersistentAIUsageBudget,
)
from careervoice_ai_web_app.persistent_usage import (
    PersistentUsageRepository,
)
from careervoice_ai_web_app.postgres_connection import (
    PostgresConnectionSettings,
    build_postgres_connection_factory,
)
from careervoice_ai_web_app.postgres_usage_repository import (
    PostgresPersistentUsageRepository,
)
from careervoice_ai_web_app.user_models import AppUser
from careervoice_ai_web_app.workflow_service import (
    CareerVoiceWorkflowService,
)

from backend.app.config import BackendSettings
from backend.app.profile_service import (
    ProfileExtractionService,
    SupportsProfileWorkflow,
)


GatewayFactory = Callable[
    [],
    SupportsOrchestratorGateway,
]


@dataclass(frozen=True)
class CareerVoiceProfileWorkflowFactory:
    """Build one user-specific CareerVoice profile workflow."""

    usage_repository: PersistentUsageRepository
    daily_ai_unit_limit: int
    gateway_factory: GatewayFactory = (
        Repo4OrchestratorGateway
    )

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> SupportsProfileWorkflow:
        """Build a workflow with persistent per-user AI usage."""
        ai_usage_budget = PersistentAIUsageBudget(
            repository=self.usage_repository,
            user=user,
            limit=self.daily_ai_unit_limit,
        )

        return CareerVoiceWorkflowService(
            self.gateway_factory(),
            ai_usage_budget=ai_usage_budget,
            output_language=output_language,
        )


def build_profile_extraction_service(
    *,
    settings: BackendSettings,
    environment: Mapping[str, str] | None = None,
) -> ProfileExtractionService | None:
    """Build persistent profile extraction for the API."""
    database_settings = (
        PostgresConnectionSettings.from_environment(
            environment
        )
    )

    if database_settings is None:
        return None

    usage_repository = (
        PostgresPersistentUsageRepository(
            build_postgres_connection_factory(
                database_settings
            )
        )
    )

    workflow_factory = (
        CareerVoiceProfileWorkflowFactory(
            usage_repository=usage_repository,
            daily_ai_unit_limit=(
                settings.daily_ai_unit_limit
            ),
        )
    )

    return ProfileExtractionService(
        workflow_factory=workflow_factory
    )