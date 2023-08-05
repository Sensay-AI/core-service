from fastapi import APIRouter

from app.routes.api_v1.endpoints import user
from app.routes.api_v1.endpoints import image_caption


router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(image_caption.router, prefix="/caption", tags=["image"])