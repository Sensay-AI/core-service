from http import HTTPStatus
from io import BytesIO

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException

from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.infrastructure.captions.replicate_caption import CaptionGenerator
from app.infrastructure.llm.caption import ChatGPTCaption
from app.models.image_caption import ImageCaption
from app.repositories.user_repository import UserNotFoundError
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.image_caption import ImageCaptionRequest
from app.schemas.users import Auth0User
from app.services.caption_service import CaptionService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/generate")
def generate_caption(
    input_data: ImageCaptionRequest,
    auth: Auth0User = Depends(check_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    caption_service: CaptionService = Depends(Provide[Container.caption_service]),
    caption_generator: CaptionGenerator = Depends(Provide[Container.caption_generator]),
    chatgpt_caption: ChatGPTCaption = Depends(Provide[Container.chatgpt_caption]),
) -> object:
    language = input_data.language
    image_url = input_data.image_url
    user_id = auth.id
    try:
        user_service.get_user_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user id provided does not exist!",
        )
    image_file = s3_service.get_file(
        file_path=image_url,
        bucket_name=s3_image_bucket,
    )
    if image_file is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The image does not exist",
        )
    image_file = BytesIO(image_file)
    caption = caption_generator.generate_from_image(
        prompt="Generate a caption for the following image", image_file=image_file
    )
    if not caption:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error generating caption",
        )
    rewritten_caption = chatgpt_caption.rewrite_caption(
        caption=caption, language=language
    )
    if not rewritten_caption:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error generating caption",
        )
    new_image_caption = ImageCaption()
    new_image_caption.user_id = user_id
    new_image_caption.image_url = image_url
    new_image_caption.caption = rewritten_caption
    return caption_service.add_image_caption(new_image_caption)
