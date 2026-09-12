"""FastAPI entry point for the CareerVoice AI backend."""

from __future__ import annotations

from collections.abc import Mapping

from fastapi import FastAPI

from backend.app.api.v1.router import (
    router as api_v1_router,
)
from backend.app.auth_runtime import (
    build_current_user_resolver,
)
from backend.app.config import BackendSettings
from backend.app.security import (
    CurrentUserResolver,
    UnconfiguredCurrentUserResolver,
)
from backend.app.usage_service import (
    DailyUsageStatusProvider,
)
from backend.app.usage_runtime import (
    build_daily_usage_status_provider,
)
from backend.app.profile_runtime import (
    build_profile_extraction_service,
)
from backend.app.profile_service import (
    ProfileExtractionProvider,
)


def create_app(
    settings: BackendSettings | None = None,
    current_user_resolver: CurrentUserResolver | None = None,
    daily_usage_status_provider: (
        DailyUsageStatusProvider | None
    ) = None,
    profile_extraction_provider: (
        ProfileExtractionProvider | None
    ) = None,
) -> FastAPI:
    """Create and configure the CareerVoice AI API."""
    resolved_settings = (
        settings
        if settings is not None
        else BackendSettings.from_environment()
    )

    application = FastAPI(
        title=resolved_settings.api_title,
        version=resolved_settings.api_version,
    )

    application.state.current_user_resolver = (
        current_user_resolver
        if current_user_resolver is not None
        else UnconfiguredCurrentUserResolver()
    )

    application.state.daily_usage_status_provider = (
        daily_usage_status_provider
    )

    application.state.profile_extraction_provider = (
        profile_extraction_provider
    )

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "careervoice-api",
        }

    application.include_router(
        api_v1_router,
        prefix="/api/v1",
    )

    return application


def create_runtime_app(
    environment: Mapping[str, str] | None = None,
) -> FastAPI:
    """Create the API using its real runtime configuration."""
    settings = BackendSettings.from_environment(
        environment
    )

    current_user_resolver = (
        build_current_user_resolver(
            environment
        )
    )

    daily_usage_status_provider = (
        build_daily_usage_status_provider(
            settings=settings,
            environment=environment,
        )
    )

    profile_extraction_provider = (
        build_profile_extraction_service(
            settings=settings,
            environment=environment,
        )
    )

    return create_app(
        settings=settings,
        current_user_resolver=current_user_resolver,
        daily_usage_status_provider=(
            daily_usage_status_provider
        ),
        profile_extraction_provider=(
            profile_extraction_provider
        ),
    )


app = create_runtime_app()