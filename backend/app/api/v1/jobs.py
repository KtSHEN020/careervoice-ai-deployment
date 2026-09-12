"""Job-search API endpoints."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel, Field

from job_listing_collector.models import NormalizedJob

from careervoice_ai_web_app.public_limits import (
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.api.v1.profile import (
    CareerProfileResponse,
)
from backend.app.job_search_service import (
    JobSearchProvider,
)
from backend.app.security import get_current_user


router = APIRouter()


class JobSearchRequest(BaseModel):
    """Reviewed profile and explicit job-search settings."""

    profile: CareerProfileResponse

    roles: list[str] = Field(
        min_length=1,
        max_length=MAX_JOB_QUERIES,
    )

    location: str | None = None

    max_results_per_role: int = Field(
        ge=1,
        le=MAX_JOB_RESULTS_PER_QUERY,
    )

    source: Literal["adzuna"] = "adzuna"

    output_language: Literal[
        "en",
        "zh-CN",
    ]


class JobSearchSettingsResponse(BaseModel):
    """Normalized settings used for one job search."""

    roles: list[str]
    location: str | None
    max_results_per_role: int
    source: Literal["adzuna"]


class JobSearchResponse(BaseModel):
    """Normalized job-search results."""

    settings: JobSearchSettingsResponse
    jobs: list[NormalizedJob]
    output_language: Literal[
        "en",
        "zh-CN",
    ]


def get_job_search_provider(
    request: Request,
) -> JobSearchProvider:
    """Return the configured job-search service."""
    provider = getattr(
        request.app.state,
        "job_search_provider",
        None,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Job search service is unavailable.",
        )

    return provider


@router.post(
    "/jobs/search",
    response_model=JobSearchResponse,
)
def search_jobs(
    payload: JobSearchRequest,
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    job_search_provider: Annotated[
        JobSearchProvider,
        Depends(get_job_search_provider),
    ],
) -> JobSearchResponse:
    """Search for jobs using the authenticated user's reviewed profile."""
    try:
        result = job_search_provider.search(
            user=current_user,
            profile=payload.profile.model_dump(),
            roles=payload.roles,
            location=payload.location,
            max_results_per_role=(
                payload.max_results_per_role
            ),
            source=payload.source,
            output_language=(
                payload.output_language
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return JobSearchResponse(
        settings=JobSearchSettingsResponse(
            roles=list(
                result.settings.roles
            ),
            location=result.settings.location,
            max_results_per_role=(
                result.settings.max_results_per_role
            ),
            source=result.settings.source,
        ),
        jobs=[
            NormalizedJob.model_validate(
                job
            )
            for job in result.jobs
        ],
        output_language=result.output_language,
    )