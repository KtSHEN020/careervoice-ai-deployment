"""Version 1 API routes."""

from fastapi import APIRouter

from backend.app.api.v1.me import router as me_router
from backend.app.api.v1.profile import (
    router as profile_router,
)
from backend.app.api.v1.usage import (
    router as usage_router,
)


router = APIRouter()

router.include_router(
    me_router,
    tags=["account"],
)

router.include_router(
    usage_router,
    tags=["usage"],
)

router.include_router(
    profile_router,
    tags=["profile"],
)