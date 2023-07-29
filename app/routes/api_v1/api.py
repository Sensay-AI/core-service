from fastapi import APIRouter

from app.routes.api_v1.endpoints import user

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
