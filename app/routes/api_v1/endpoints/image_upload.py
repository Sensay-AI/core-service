import io
from http import HTTPStatus

from PIL import Image
from fastapi import UploadFile, APIRouter, HTTPException
from app.aws.s3 import S3Image
from app.core import config

router = APIRouter()
s3Client = S3Image()


@router.post("/uploadimage")
async def upload_image_to_s3(
    image_file: UploadFile,
    user_id: str
) -> dict[str, str]:
    image_file.file.seek(0)
    contents = image_file.file.read()
    temp_file = io.BytesIO()
    temp_file.write(contents)
    temp_file.seek(0)

    try:
        img = Image.open(temp_file)
        img.verify()
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Not a valid image"
        )
    result = s3Client.upload_file(file=temp_file,
                                  bucket_name=config.S3_IMAGE_BUCKET,
                                  user_id=user_id
                                  )
    if result is not None:
        return {"upload path": result}
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="We have an error uploading files"
    )
