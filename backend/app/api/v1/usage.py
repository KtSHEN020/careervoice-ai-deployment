"""Daily usage API endpoints."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel

from careervoice_ai_web_app.user_models import AppUser

from backend.app.security import get_current_user
from backend.app.usage_service import (
    DailyUsageStatusProvider,
)


router = APIRouter()


class DailyUsageResponse(BaseModel):
    """Public daily usage information for the current user."""

    usage_date: date
    daily_ai_unit_limit: int
    ai_units_used: int
    remaining_ai_units: int
    ai_profile_extractions: int
    voice_transcriptions: int
    document_recognitions: int
    ai_ranking_runs: int
    job_searches: int


def get_daily_usage_status_provider(
    request: Request,
) -> DailyUsageStatusProvider:
    """Return the configured daily usage service."""
    provider = getattr(
        request.app.state,
        "daily_usage_status_provider",
        None,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Usage service is unavailable.",
        )

    return provider


@router.get(
    "/usage",
    response_model=DailyUsageResponse,
)
def get_usage(
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    usage_provider: Annotated[
        DailyUsageStatusProvider,
        Depends(get_daily_usage_status_provider),
    ],
) -> DailyUsageResponse:
    """Return today's usage status for the authenticated user."""
    usage = usage_provider.get_status(
        current_user
    )

    return DailyUsageResponse(
        usage_date=usage.usage_date,
        daily_ai_unit_limit=usage.daily_ai_unit_limit,
        ai_units_used=usage.ai_units_used,
        remaining_ai_units=usage.remaining_ai_units,
        ai_profile_extractions=(
            usage.ai_profile_extractions
        ),
        voice_transcriptions=(
            usage.voice_transcriptions
        ),
        document_recognitions=(
            usage.document_recognitions
        ),
        ai_ranking_runs=usage.ai_ranking_runs,
        job_searches=usage.job_searches,
    )