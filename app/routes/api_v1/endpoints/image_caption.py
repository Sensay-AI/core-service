from io import BytesIO

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.models.image_caption import ImageCaption
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.image_caption import ImageCaptionRequest
from app.schemas.users import Auth0User
from app.services.caption_service import CaptionService

router = APIRouter()


@router.post("/generate_caption")
def generate_caption(
    input_data: ImageCaptionRequest,
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    caption_service: CaptionService = Depends(Provide[Container.caption_service])
) -> object:
    language = input_data.language
    image_url = input_data.image_url
    image_file = s3_service.get_file(
        file_path=image_url,
        bucket_name=s3_image_bucket,
    )
    image_file = BytesIO(image_file)

    caption = caption_service.get_caption_from_image(image_file, language)

    new_image_caption = ImageCaption()
    new_image_caption.user_id = auth.id
    new_image_caption.image_url = image_url
    new_image_caption.caption = caption
    return caption_service.add_image_caption(new_image_caption)
