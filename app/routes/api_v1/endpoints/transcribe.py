from fastapi import APIRouter,  Depends, HTTPException, UploadFile, status

# from google.cloud import speech #Import v2 version
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
# import soundfile as sf

import base64
import json

from app.schemas.users import Auth0User
from app.container.containers import Container
from app.routes.api_v1.endpoints.auth import check_user
from dependency_injector.wiring import Provide, inject


#Router initialize
router = APIRouter()
# logger = logging.getLogger()

# Decode Google file credentials
# Need add to config
encoded_credentials = ""
decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
temp_credentials_path = "temp_credentials.json"
with open(temp_credentials_path, "w") as temp_file:
    temp_file.write(decoded_credentials)

project_id = "" # Need add to config

@router.post("/transcribe")
async def transcribe_audio (language_code: str, file: UploadFile) -> object:
    """Transcribe an audio file."""
    # Instantiates a client
    audioFileType = file.content_type
    client = SpeechClient.from_service_account_file(temp_credentials_path)

    # Check if the uploaded file is an audio file
    if not audioFileType.startswith("audio/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not an audio file")
    # Check if the uploaded file is not belongs endcoding FLAC or LINEAR16
    if not (audioFileType == "audio/flac" or audioFileType == "audio/wav"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not FLAC or LINEAR16 audio")
    
    # Reads a file as bytes
    audio_content = await file.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[language_code],
        model="long", 
        # Reference: https://cloud.google.com/speech-to-text/v2/docs/transcription-model
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,
        ),
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    transcriptions = [result.alternatives[0].transcript for result in response.results]

    return {"transcriptions": transcriptions}
