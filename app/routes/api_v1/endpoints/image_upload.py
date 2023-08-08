import io
from http import HTTPStatus
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.aws.s3 import S3Image
from app.core import config
from app.core.auth0 import check_user
from app.schemas.users import Auth0User

router = APIRouter()


@router.post("/upload")
async def upload_image_to_s3(
    image_file: UploadFile, user_id: str, auth: Auth0User = Depends(check_user)
) -> Dict[str, str]:
    if not image_file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="the file you uploaded was not a valid image",
        )
    image_file.file.seek(0)
    contents = image_file.file.read()
    temp_file = io.BytesIO()
    temp_file.write(contents)
    temp_file.seek(0)

    try:
        Image.open(temp_file)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Your image is corrupted or damaged",
        )
    result = S3Image().s3_client.upload_file(
        file=temp_file, bucket_name=config.S3_IMAGE_BUCKET, user_id=user_id
    )
    if result:
        return {"upload_path": result}
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="We have an error uploading files",
    )
