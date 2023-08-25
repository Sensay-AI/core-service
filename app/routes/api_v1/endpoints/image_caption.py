from io import BytesIO

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.models.schemas.users import Auth0User
from app.routes.api_v1.endpoints.auth import check_user
from app.models.schemas.image_caption import ImageCaptionRequest
from app.services.caption_service import CaptionService

router = APIRouter()


@router.post("/generate_caption")
@inject
def generate_caption(
    input_data: ImageCaptionRequest,
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    caption_service: CaptionService = Depends(Provide[Container.caption_service]),
) -> object:
    image_path = input_data.image_bucket_path_key
    image_file = s3_service.get_file(
        file_path=image_path,
        bucket_name=s3_image_bucket,
    )
    image_file = BytesIO(image_file)
    caption_input = {"file": image_file, "path": image_path, **input_data.dict()}
    return StreamingResponse(
        caption_service.get_caption_from_image(
            user_id=auth.id, caption_input=caption_input
        ),
        media_type="text/plain",
    )
