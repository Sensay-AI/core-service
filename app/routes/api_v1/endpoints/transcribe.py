""" Transcribe api """
import io

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.container.containers import Container
from app.infrastructure.aws.s3 import S3Service
from app.infrastructure.gcp.speech2text import Speech2Text
from app.routes.api_v1.endpoints.auth import check_user
from app.schemas.users import Auth0User

# Router initialize
router = APIRouter()


@router.post("/")
@inject
async def transcribe_audio(
    language_code: str,
    audio_file: UploadFile,
    project_id: str = Depends(Provide[Container.google_project_id]),
    gcp_credentials: str = Depends(Provide[Container.google_credential_file]),
    auth: Auth0User = Depends(check_user),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_audio_bucket: str = Depends(Provide[Container.s3_audio_bucket]),
) -> object:
    """Transcribe an audio file."""
    # Check if the uploaded file is an audio mp3 file
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

    # Reads a file as bytes
    audio_content = await audio_file.read()

    # Save audio to S3
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

    speech_to_text = Speech2Text(gcp_credentials)

    response_transcribe = speech_to_text.transcribe_audio(
        project_id=project_id, language_code=language_code, audio_content=audio_content
    )

    return {"transcriptions": response_transcribe, "audio_url": audio_url}
