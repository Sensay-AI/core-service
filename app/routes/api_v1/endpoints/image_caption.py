<<<<<<< HEAD
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
=======
import io
from io import BytesIO
from http import HTTPStatus
from io import BytesIO
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.aws.s3 import S3Image
from app.captions.replicate_caption import CaptionGenerator
from app.chatgpt.chatgpt_requests import rewrite_caption_in_language
from app.core import config
from app.db.database import get_db
from app.models.image_caption import ImageCaptionRequest, UserImage

router = APIRouter()
s3Client = S3Image()
captionGen = CaptionGenerator()
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)


@router.post("/generate")
def generate_caption(
    input_data: ImageCaptionRequest,
<<<<<<< HEAD
    db: Session = Depends(get_db),
    auth: Auth0User = Depends(check_user),
) -> Dict[str, str]:
    language = input_data.language
    image_url = input_data.image_url
    user_id = input_data.user_id
    user_exist = db.query(UserInfo).filter(UserInfo.user_id == user_id).first()
    if not user_exist:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user id provided does not exist!",
        )
    image_file = S3Image().s3_client.get_file(
        file_path=image_url, bucket_name=config.S3_IMAGE_BUCKET
    )
    if image_file:
=======
    db: Session = Depends(get_db)
) -> dict[str, str]:
    user_id = input_data.user_id
    language = input_data.language
    image_url = input_data.image_url
    image_file = s3Client.get_file(file_path=image_url,
                                   bucket_name=config.S3_IMAGE_BUCKET
                                   )
    if image_file is not None:
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
        image_file = image_file["Body"].read()
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="The image does not exist",
        )
    image_file = BytesIO(image_file)
<<<<<<< HEAD
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
=======
    caption = captionGen.generate_from_image(
        prompt="generate a caption for the following image",
        image_file=image_file
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
    user_image_caption = (
        db.query(UserImage).filter(UserImage.user_id == user_id).first()
    )
    new_image_caption = {
        "language": language,
        "image_url": input_data.image_url,
        "caption": rewritten_caption,
    }
    if user_image_caption is not None:
        user_image_caption.captioned_images.append(new_image_caption)
    else:
        new_user_image = UserImage()
        new_user_image.user_id = user_id
        new_user_image.captioned_images = [new_image_caption]
        db.add(new_user_image)
    db.commit()
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
    return {"caption": rewritten_caption}
