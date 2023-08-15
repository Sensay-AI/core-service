from fastapi import APIRouter

from app.routes.api_v1.endpoints import auth, image_upload, user
from app.routes.api_v1.endpoints import image_caption, user

router = APIRouter()
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(image_upload.router, prefix="/image", tags=["image"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(image_caption.router, prefix="/caption", tags=["image"])
