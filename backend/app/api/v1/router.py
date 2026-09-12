"""Version 1 API routes."""

from fastapi import APIRouter

from backend.app.api.v1.me import router as me_router


router = APIRouter()

router.include_router(
    me_router,
    tags=["account"],
)