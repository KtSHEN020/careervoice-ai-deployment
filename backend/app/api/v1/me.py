"""Current-user API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from careervoice_ai_web_app.user_models import AppUser

from backend.app.security import get_current_user


router = APIRouter()


class CurrentUserResponse(BaseModel):
    """Public CareerVoice account information for the current user."""

    id: UUID
    email: str
    enabled: bool


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    current_user: Annotated[
        AppUser,
        Depends(get_current_user),
    ],
) -> CurrentUserResponse:
    """Return the authenticated CareerVoice user."""
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        enabled=current_user.enabled,
    )