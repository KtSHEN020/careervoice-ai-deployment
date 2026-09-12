"""Career profile API endpoints."""

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
    Field,
    field_validator,
)

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.public_limits import (
    MAX_CAREER_TEXT_CHARACTERS,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.profile_service import (
    ProfileExtractionProvider,
)
from backend.app.security import get_current_user


router = APIRouter()


class TextProfileExtractionRequest(BaseModel):
    """Text input used to create a structured career profile."""

    career_preference_text: str = Field(
        min_length=1,
        max_length=MAX_CAREER_TEXT_CHARACTERS,
    )
    extractor: Literal[
        "rules",
        "llm",
    ]
    output_language: Literal[
        "en",
        "zh-CN",
    ]

    @field_validator(
        "career_preference_text"
    )
    @classmethod
    def reject_blank_career_text(
        cls,
        value: str,
    ) -> str:
        """Reject text containing only whitespace."""
        if not value.strip():
            raise ValueError(
                "Career information cannot be empty."
            )

        return value


class CareerProfileResponse(BaseModel):
    """Canonical structured CareerVoice career profile."""

    target_roles: list[str]
    skills: list[str]
    experience_level: str | None
    preferred_locations: list[str]
    preferred_work_types: list[str]
    liked_areas: list[str]
    disliked_areas: list[str]
    hard_constraints: list[str]
    career_goals: list[str]
    notes: list[str]


class TextProfileExtractionResponse(BaseModel):
    """Result returned after extracting a career profile."""

    profile: CareerProfileResponse
    extractor: Literal[
        "rules",
        "llm",
    ]
    output_language: Literal[
        "en",
        "zh-CN",
    ]


def get_profile_extraction_provider(
    request: Request,
) -> ProfileExtractionProvider:
    """Return the configured profile extraction service."""
    provider = getattr(
        request.app.state,
        "profile_extraction_provider",
        None,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile extraction service is unavailable.",
        )

    return provider


@router.post(
    "/profile/extract",
    response_model=TextProfileExtractionResponse,
)
def extract_text_profile(
    payload: TextProfileExtractionRequest,
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    profile_provider: Annotated[
        ProfileExtractionProvider,
        Depends(get_profile_extraction_provider),
    ],
) -> TextProfileExtractionResponse:
    """Extract a career profile from authenticated user text."""
    try:
        result = profile_provider.extract_text(
            user=current_user,
            career_preference_text=(
                payload.career_preference_text
            ),
            extractor=payload.extractor,
            output_language=payload.output_language,
        )
    except AIUsageLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Daily AI allowance is insufficient "
                "for this request."
            ),
        ) from exc

    return TextProfileExtractionResponse(
        profile=CareerProfileResponse(
            **result.profile
        ),
        extractor=result.extractor,
        output_language=result.output_language,
    )