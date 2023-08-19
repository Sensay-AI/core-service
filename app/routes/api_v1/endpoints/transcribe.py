""" Transcribe api """
import base64

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

from app.container.containers import Container

# Router initialize
router = APIRouter()


@router.post("/")
@inject
async def transcribe_audio(
    language_code: str,
    file: UploadFile,
    project_id: str = Depends(Provide[Container.google_project_id]),
    gcp_credentials: str = Depends(Provide[Container.google_credential_file]),
) -> object:
    """Transcribe an audio file."""
    decoded_gcp_credentials = base64.b64decode(gcp_credentials).decode("utf-8")
    temp_credentials_path = "temp_credentials.json"
    with open(temp_credentials_path, "w", encoding="utf-8") as temp_file:
        temp_file.write(decoded_gcp_credentials)

    audio_file_type = file.content_type
    # Connect to Google Cloud Platform file
    client = SpeechClient.from_service_account_file(temp_credentials_path)

    # Check if the uploaded file is an audio mp3 file
    if audio_file_type not in ["audio/mpeg", "audio/flac", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )
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

    recogniser_gcp = f"projects/{project_id}/locations/global/recognizers/_".format(
        project_id=project_id
    )
    request = cloud_speech.RecognizeRequest(
        recognizer=recogniser_gcp,
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    transcriptions = [result.alternatives[0].transcript for result in response.results]

    response_transcribe = "".join(transcriptions)

    return {"transcriptions": response_transcribe}
