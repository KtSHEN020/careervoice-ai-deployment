from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Protocol, TypeVar

from careervoice_ai_orchestrator import api as orchestrator_api
from careervoice_ai_orchestrator.command_runner import (
    CommandNotFoundError,
    CommandRunError,
)
from careervoice_ai_orchestrator.models import WorkflowConfig

from careervoice_ai_web_app.errors import OrchestrationError

ResultT = TypeVar("ResultT")


class SupportsOrchestratorGateway(Protocol):
    """Interface used by web workflow services to access Repo 4."""

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        """Extract or load a structured career profile."""

    def save_career_profile(
        self,
        profile: Mapping[str, object],
        profile_path: str | Path,
    ) -> Path:
        """Save a reviewed career profile."""

    def resolve_queries(self, config: WorkflowConfig) -> tuple[str, ...]:
        """Resolve explicit or profile-derived job queries."""

    def collect_jobs(self, config: WorkflowConfig) -> list[dict[str, object]]:
        """Collect and return normalized job listings."""

    def generate_recommendations(
        self,
        config: WorkflowConfig,
    ) -> dict[str, object]:
        """Generate and return the recommendation document."""


class Repo4OrchestratorGateway:
    """Adapter between Repo 5 and Repo 4's public staged API."""

    def extract_profile(
        self,
        config: WorkflowConfig,
        *,
        profile_input_text: str | None = None,
    ) -> dict[str, object]:
        result = self._run_stage(
            stage="profile extraction",
            failure_message="Career profile extraction could not be completed.",
            action=lambda: orchestrator_api.extract_profile(
                config,
                profile_input_text=profile_input_text,
            ),
        )
        return result.profile

    def save_career_profile(
        self,
        profile: Mapping[str, object],
        profile_path: str | Path,
    ) -> Path:
        return self._run_stage(
            stage="profile saving",
            failure_message="The reviewed career profile could not be saved.",
            action=lambda: orchestrator_api.save_career_profile(
                profile,
                profile_path,
            ),
        )

    def resolve_queries(self, config: WorkflowConfig) -> tuple[str, ...]:
        return self._run_stage(
            stage="query resolution",
            failure_message="Job-search roles could not be resolved.",
            action=lambda: orchestrator_api.resolve_queries(config),
        )

    def collect_jobs(self, config: WorkflowConfig) -> list[dict[str, object]]:
        result = self._run_stage(
            stage="job collection",
            failure_message="Job collection could not be completed.",
            action=lambda: orchestrator_api.collect_jobs(config),
        )
        return result.jobs

    def generate_recommendations(
        self,
        config: WorkflowConfig,
    ) -> dict[str, object]:
        result = self._run_stage(
            stage="recommendation generation",
            failure_message="Recommendations could not be generated.",
            action=lambda: orchestrator_api.generate_recommendations(config),
        )
        return result.recommendations

    @staticmethod
    def _run_stage(
        *,
        stage: str,
        failure_message: str,
        action: Callable[[], ResultT],
    ) -> ResultT:
        try:
            return action()
        except CommandNotFoundError as error:
            raise OrchestrationError(
                stage=stage,
                user_message=(
                    "A required CareerVoice AI component is not installed in "
                    "the web application environment."
                ),
                technical_details=str(error),
            ) from error
        except CommandRunError as error:
            raise OrchestrationError(
                stage=stage,
                user_message=failure_message,
                technical_details=str(error),
            ) from error
        except ValueError as error:
            raise OrchestrationError(
                stage=stage,
                user_message=str(error),
                technical_details=str(error),
            ) from error
        except OSError as error:
            raise OrchestrationError(
                stage=stage,
                user_message=failure_message,
                technical_details=str(error),
            ) from error