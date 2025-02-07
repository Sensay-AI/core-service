from fastapi import APIRouter

from app.routes.api_v1.endpoints import (
    auth,
    difficulty_level,
    image,
    language,
    user,
    vocabulary,
)

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(image.router, prefix="/image", tags=["image"])
router.include_router(
    vocabulary.router, prefix="/lesson/vocabulary", tags=["vocabulary"]
)
router.include_router(language.router, prefix="/language", tags=["language"])
router.include_router(
    difficulty_level.router,
    prefix="/lesson/difficulty_level",
    tags=["difficulty_level"],
)
