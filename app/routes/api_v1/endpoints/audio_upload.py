import io
from typing import Dict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.users import Auth0User

#
router = APIRouter()


@router.post("/upload")
@inject
def upload_audio_to_s3(
    audio_file: UploadFile,
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_audio_bucket: str = Depends(Provide[Container.s3_audio_bucket]),
) -> Dict[str, str]:
    """Upload audio file to S3"""
    audio_file_type = audio_file.content_type
    if audio_file_type not in ["audio/mpeg", "audio/flac", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )
    if audio_file_type == "audio/mpeg":
        file_extension = ".mp3"
    elif audio_file_type == "audio/flac":
        file_extension = ".flac"
    else:
        file_extension = ".wav"

    audio_file.file.seek(0)
    contents = audio_file.file.read()
    temp_file = io.BytesIO()
    temp_file.write(contents)
    temp_file.seek(0)

    audio_url = s3_service.upload_file(
        file=temp_file,
        bucket_name=s3_audio_bucket,
        user_id=auth.id,
        extension=file_extension,
    )
    if audio_url is None or audio_url == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We have an error uploading files",
        )

    return {"audio_url": audio_url}
