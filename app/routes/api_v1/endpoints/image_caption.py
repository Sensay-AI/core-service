from http import HTTPStatus
from io import BytesIO
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.aws.s3 import S3Image
from app.captions.replicate_caption import CaptionGenerator
from app.chatgpt.chatgpt_requests import rewrite_caption_in_language
from app.core import config
from app.core.auth0 import check_user
from app.db.database import get_db
from app.models.image_caption import ImageCaption, ImageCaptionRequest
from app.models.users import UserInfo
from app.schemas.users import Auth0User

router = APIRouter()


@router.post("/generate")
def generate_caption(
    input_data: ImageCaptionRequest,
    db: Session = Depends(get_db),
    auth: Auth0User = Depends(check_user),
) -> Dict[str, str]:
    language = input_data.language
    image_url = input_data.image_url
    user_id = auth.id
    image_file = S3Image().s3_client.get_file(
        file_path=image_url, bucket_name=config.S3_IMAGE_BUCKET
    )
    if image_file:

        image_file = image_file["Body"].read()
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The image does not exist",
        )
    image_file = BytesIO(image_file)
    caption = CaptionGenerator().generate_from_image(
        prompt="Generate a caption for the following image", image_file=image_file
    )
    if not caption:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error generating caption",
        )
    rewritten_caption = rewrite_caption_in_language(caption=caption, language=language)
    if not rewritten_caption:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error generating caption",
        )
    new_image_caption = ImageCaption()
    new_image_caption.user_id = user_id
    new_image_caption.image_url = image_url
    new_image_caption.rewritten_caption = rewritten_caption
    db.add(new_image_caption)
    db.commit()
    db.refresh(new_image_caption)
    return {"caption": rewritten_caption}
