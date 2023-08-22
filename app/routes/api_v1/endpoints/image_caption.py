from io import BytesIO

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse


from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.models.db.image_caption import ImageCaption
from app.routes.api_v1.endpoints.auth import check_user
from app.models.schemas.image_caption import ImageCaptionRequest, CaptionInput
from app.models.schemas.users import Auth0User
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
    caption_input = CaptionInput(
        image_file=image_file,
        image_path=image_url
    )
    return StreamingResponse(
        caption_service.get_caption_from_image(
            user_id=auth.id,
            caption_input=caption_input,
            language=language
        ),
        media_type="text/plain",
    )
