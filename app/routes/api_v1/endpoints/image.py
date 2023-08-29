import io
import pathlib
from http import HTTPStatus
from io import BytesIO
from typing import Dict, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError

from app.container.containers import Container
from app.infrastructure.aws.s3 import (
    S3FilesInFolderResponse,
    S3Service,
    UploadS3FileResponse,
)
from app.models.schemas.image_caption import ImageCaptionRequest
from app.models.schemas.users import Auth0User
from app.routes.api_v1.endpoints.auth import check_user
from app.services.caption_service import CaptionService

#
router = APIRouter()


@router.post("")
@inject
async def upload_image_to_s3(
    image_file: UploadFile,
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
) -> UploadS3FileResponse:
    file_extension = pathlib.Path(image_file.filename).suffix
    if file_extension not in [".png", ".jpg", ".jpeg"]:
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
    result = s3_service.upload_file(
        file=temp_file,
        bucket_name=s3_image_bucket,
        user_id=auth.id,
        extension=file_extension,
    )
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="We have an error uploading files",
    )


@router.get("")
@inject
async def get_user_uploaded_images(
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
) -> Dict[str, List[S3FilesInFolderResponse]]:
    return {
        "items": s3_service.list_s3_files_in_folder(
            bucket_name=s3_image_bucket,
            user_id=auth.id,
        )
    }


@router.post("/caption")
@inject
async def generate_caption(
    input_data: ImageCaptionRequest,
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    caption_service: CaptionService = Depends(Provide[Container.caption_service]),
) -> object:
    image_file = s3_service.get_file(
        file_path=input_data.image_bucket_path_key,
        bucket_name=s3_image_bucket,
    )
    image_file = BytesIO(image_file)
    caption_input = {
        "file": image_file,
        "path": input_data.image_bucket_path_key,
        **input_data.dict(),
    }
    return StreamingResponse(
        caption_service.get_caption_from_image(
            user_id=auth.id, caption_input=caption_input
        ),
        media_type="text/plain",
    )


@router.get("/caption")
@inject
async def get_caption_history(
    auth: Auth0User = Depends(check_user),
    caption_service: CaptionService = Depends(Provide[Container.caption_service]),
) -> object:
    return caption_service.list_caption_history(user_id=auth.id)
