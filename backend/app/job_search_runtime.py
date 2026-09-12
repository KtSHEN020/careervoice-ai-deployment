"""Runtime construction for CareerVoice job searching."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from careervoice_ai_web_app.orchestrator_gateway import (
    Repo4OrchestratorGateway,
    SupportsOrchestratorGateway,
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
from backend.app.job_search_service import (
    JobSearchService,
    SupportsJobSearchWorkflow,
)
from backend.app.job_search_usage import (
    PersistentJobSearchUsageRecorder,
)


GatewayFactory = Callable[
    [],
    SupportsOrchestratorGateway,
]


@dataclass(frozen=True)
class CareerVoiceJobSearchWorkflowFactory:
    """Build one CareerVoice workflow for authenticated job searching."""

    gateway_factory: GatewayFactory = (
        Repo4OrchestratorGateway
    )

    def __call__(
        self,
        *,
        user: AppUser,
        output_language: str,
    ) -> SupportsJobSearchWorkflow:
        """Build a job-search workflow for one authenticated request."""
        del user

        return CareerVoiceWorkflowService(
            self.gateway_factory(),
            output_language=output_language,
        )


def build_job_search_service(
    *,
    settings: BackendSettings,
    environment: Mapping[str, str] | None = None,
) -> JobSearchService | None:
    """Build persistent job searching for the API."""
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
        CareerVoiceJobSearchWorkflowFactory()
    )

    usage_recorder = (
        PersistentJobSearchUsageRecorder(
            repository=usage_repository,
            daily_ai_unit_limit=(
                settings.daily_ai_unit_limit
            ),
        )
    )

    return JobSearchService(
        workflow_factory=workflow_factory,
        usage_recorder=usage_recorder,
    )