""" Transcribe api """
from typing import Dict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from google.cloud.speech_v2.types import cloud_speech

from app.container.containers import Container
from app.infrastructure.gcp.speech2text import Speech2Text

# Router initialize
router = APIRouter()


@router.post("/")
@inject
async def transcribe_audio(
    language_code: str,
    audio_file: UploadFile,
    google_recogniser: str = Depends(Provide[Container.google_recogniser]),
    gcp_credentials: str = Depends(Provide[Container.google_credential_file]),
    auth: Auth0User = Depends(check_user),
) -> Dict[str, str]:
    """Transcribe an audio file."""

    # Check if the uploaded file is an audio mp3 file
    audio_file_type = audio_file.content_type
    if audio_file_type not in ["audio/mpeg", "audio/flac", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )

    # Reads a file as bytes
    audio_content = await audio_file.read()

    # Configuration speech to text
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[language_code],
        model="long",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,
        ),
    )

    speech_to_text = Speech2Text(gcp_credentials, google_recogniser, config=config)

    response_transcribe = speech_to_text.transcribe_audio(audio_content=audio_content)

    return {"transcriptions": response_transcribe}
