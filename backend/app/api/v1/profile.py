"""Career profile API endpoints."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)

from starlette.concurrency import run_in_threadpool

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from careervoice_ai_web_app.ai_usage import (
    AIUsageLimitError,
)
from careervoice_ai_web_app.document_input import (
    MAX_DOCUMENT_BYTES,
)
from careervoice_ai_web_app.public_limits import (
    MAX_ADDITIONAL_PREFERENCES_CHARACTERS,
    MAX_CAREER_TEXT_CHARACTERS,
)
from careervoice_ai_web_app.user_models import AppUser

from backend.app.profile_service import (
    ProfileExtractionProvider,
)
from backend.app.security import get_current_user

from careervoice_ai_web_app.voice_input import (
    MAX_VOICE_RECORDING_BYTES,
)

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

class VoiceTranscriptionResponse(BaseModel):
    """Text returned after transcribing browser-recorded audio."""

    text: str

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
            detail=(
                "Profile extraction service is unavailable."
            ),
        )

    return provider


def build_profile_response(
    *,
    profile: dict[str, object],
    extractor: str,
    output_language: str,
) -> TextProfileExtractionResponse:
    """Build the canonical API response for profile extraction."""
    return TextProfileExtractionResponse(
        profile=CareerProfileResponse(
            **profile
        ),
        extractor=extractor,
        output_language=output_language,
    )


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

    return build_profile_response(
        profile=result.profile,
        extractor=result.extractor,
        output_language=result.output_language,
    )


@router.post(
    "/profile/extract-document",
    response_model=TextProfileExtractionResponse,
)
async def extract_document_profile(
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    profile_provider: Annotated[
        ProfileExtractionProvider,
        Depends(get_profile_extraction_provider),
    ],
    document: Annotated[
        UploadFile,
        File(),
    ],
    extractor: Annotated[
        Literal[
            "rules",
            "llm",
        ],
        Form(),
    ],
    output_language: Annotated[
        Literal[
            "en",
            "zh-CN",
        ],
        Form(),
    ],
    additional_preferences: Annotated[
        str,
        Form(
            max_length=(
                MAX_ADDITIONAL_PREFERENCES_CHARACTERS
            )
        ),
    ] = "",
    allow_image_recognition: Annotated[
        bool,
        Form(),
    ] = False,
) -> TextProfileExtractionResponse:
    """Extract a career profile from an uploaded document."""
    try:
        content = await document.read(
            MAX_DOCUMENT_BYTES + 1
        )
    finally:
        await document.close()

    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                "The uploaded document is too large. "
                "The maximum supported size is 5 MB."
            ),
        )

    filename = (
        document.filename or ""
    ).strip()

    try:
        result = await run_in_threadpool(
            profile_provider.extract_document,
            user=current_user,
            filename=filename,
            content=content,
            additional_preferences=(
                additional_preferences
            ),
            extractor=extractor,
            output_language=output_language,
            allow_image_recognition=(
                allow_image_recognition
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

    return build_profile_response(
        profile=result.profile,
        extractor=result.extractor,
        output_language=result.output_language,
    )


@router.post(
    "/profile/transcribe-voice",
    response_model=VoiceTranscriptionResponse,
)
async def transcribe_voice_profile_input(
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
    profile_provider: Annotated[
        ProfileExtractionProvider,
        Depends(get_profile_extraction_provider),
    ],
    recording: Annotated[
        UploadFile,
        File(),
    ],
    output_language: Annotated[
        Literal[
            "en",
            "zh-CN",
        ],
        Form(),
    ],
) -> VoiceTranscriptionResponse:
    """Transcribe authenticated browser voice input."""
    filename = (
        recording.filename or ""
    ).strip()

    media_type = (
        recording.content_type or ""
    ).strip()

    try:
        content = await recording.read(
            MAX_VOICE_RECORDING_BYTES + 1
        )
    finally:
        await recording.close()

    if (
        len(content)
        > MAX_VOICE_RECORDING_BYTES
    ):
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                "The voice recording is too large. "
                "The maximum supported size is 10 MB."
            ),
        )

    try:
        result = await run_in_threadpool(
            profile_provider.transcribe_voice,
            user=current_user,
            filename=filename,
            content=content,
            media_type=media_type,
            output_language=output_language,
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

    return VoiceTranscriptionResponse(
        text=result.text,
    )