"""Job recommendation API endpoints."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from job_listing_collector.models import (
    NormalizedJob,
)

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.public_limits import (
    MAX_JOB_QUERIES,
    MAX_JOB_RESULTS_PER_QUERY,
    MAX_RECOMMENDATIONS,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.api.v1.profile import (
    CareerProfileResponse,
)
from backend.app.recommendation_service import (
    RecommendationProvider,
)
from backend.app.security import get_current_user


router = APIRouter()


MAX_RECOMMENDATION_INPUT_JOBS = (
    MAX_JOB_QUERIES
    * MAX_JOB_RESULTS_PER_QUERY
)


class RecommendationRequest(BaseModel):
    """Reviewed profile, jobs, and ranking settings."""

    profile: CareerProfileResponse

    jobs: list[NormalizedJob] = Field(
        min_length=1,
        max_length=MAX_RECOMMENDATION_INPUT_JOBS,
    )

    scorer: Literal[
        "rules",
        "llm",
    ]

    max_results: int = Field(
        ge=1,
        le=MAX_RECOMMENDATIONS,
    )

    exclude_rejected: bool = False

    output_language: Literal[
        "en",
        "zh-CN",
    ]


class RecommendationSettingsResponse(BaseModel):
    """Normalized settings used for recommendation generation."""

    scorer: Literal[
        "rules",
        "llm",
    ]
    max_results: int
    exclude_rejected: bool


class RecommendationItemResponse(BaseModel):
    """One structured CareerVoice job recommendation."""

    model_config = ConfigDict(
        extra="allow"
    )

    job_id: str = ""
    title: str = ""
    company: str = ""

    match_score: int = Field(
        ge=0,
        le=100,
    )

    recommendation_level: str = ""

    reasons: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    penalties: list[str] = Field(
        default_factory=list
    )

    uncertainties: list[str] = Field(
        default_factory=list
    )

    is_rejected_by_constraints: bool

    scoring_method: Literal[
        "rules",
        "llm",
    ]

    score_breakdown: dict[str, object] = Field(
        default_factory=dict
    )

    matched_details: dict[str, object] = Field(
        default_factory=dict
    )


class RecommendationResponse(BaseModel):
    """Structured recommendation results."""

    settings: RecommendationSettingsResponse

    recommendations: list[
        RecommendationItemResponse
    ]

    total_jobs_scored: int
    total_jobs_scored_with_llm: int | None = None
    llm_candidate_limit: int | None = None
    total_recommendations_returned: int

    scoring_method: Literal[
        "rules",
        "llm",
    ]

    output_language: Literal[
        "en",
        "zh-CN",
    ]


def get_recommendation_provider(
    request: Request,
) -> RecommendationProvider:
    """Return the configured recommendation service."""
    provider = getattr(
        request.app.state,
        "recommendation_provider",
        None,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation service is unavailable.",
        )

    return provider


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
)
def generate_recommendations(
    payload: RecommendationRequest,
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    recommendation_provider: Annotated[
        RecommendationProvider,
        Depends(get_recommendation_provider),
    ],
) -> RecommendationResponse:
    """Generate ranked job recommendations for the current user."""
    try:
        result = recommendation_provider.recommend(
            user=current_user,
            profile=payload.profile.model_dump(),
            jobs=[
                job.model_dump(
                    mode="json"
                )
                for job in payload.jobs
            ],
            scorer=payload.scorer,
            max_results=payload.max_results,
            exclude_rejected=(
                payload.exclude_rejected
            ),
            output_language=(
                payload.output_language
            ),
        )
    except AIUsageLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Daily AI allowance is insufficient "
                "for this request."
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    document = result.document.document

    return RecommendationResponse(
        settings=RecommendationSettingsResponse(
            scorer=result.settings.scorer,
            max_results=(
                result.settings.max_results
            ),
            exclude_rejected=(
                result.settings.exclude_rejected
            ),
        ),
        recommendations=[
            RecommendationItemResponse.model_validate(
                recommendation
            )
            for recommendation
            in result.document.recommendations
        ],
        total_jobs_scored=(
            result.document.total_jobs_scored
        ),
        total_jobs_scored_with_llm=(
            document.get(
                "total_jobs_scored_with_llm"
            )
        ),
        llm_candidate_limit=(
            document.get(
                "llm_candidate_limit"
            )
        ),
        total_recommendations_returned=(
            result.document.total_recommendations_returned
        ),
        scoring_method=(
            result.document.scoring_method
        ),
        output_language=(
            result.output_language
        ),
    )