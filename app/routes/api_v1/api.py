from fastapi import APIRouter

from app.routes.api_v1.endpoints import user, vocabulary

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(
    vocabulary.router, prefix="/lesson/vocabulary", tags=["vocabulary"]
)
