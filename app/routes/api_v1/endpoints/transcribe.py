from fastapi import APIRouter,  Depends, HTTPException, UploadFile, status
from google.cloud import speech #Import v1 version
from dependency_injector.wiring import Provide, inject
import base64
import json
from app.schemas.users import Auth0User
from app.container.containers import Container
from app.routes.api_v1.endpoints.auth import check_user


#Router initialize
router = APIRouter()
# logger = logging.getLogger()

# Decode Google file credentials
encoded_credentials = ""
decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
temp_credentials_path = "temp_credentials.json"
with open(temp_credentials_path, "w") as temp_file:
    temp_file.write(decoded_credentials)
    
# Create client to connect to Google Cloud Speech to text api.
client = speech.SpeechClient.from_service_account_json(temp_credentials_path)

# auth: Auth0User = Depends(check_user)
@router.post("/transcribe")
async def transcribe_audio (language_code: str, file: UploadFile) -> object:
    audioFileType = file.content_type
    # Check if the uploaded file is an audio file
    if not audioFileType.startswith("audio/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not an audio file")
    # Check if the uploaded file is not belongs endcoding FLAC or LINEAR16
    if not (audioFileType == "audio/flac" or audioFileType == "audio/wav"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not FLAC or LINEAR16 audio")
    
    # Set sample rate hertz
    if (audioFileType == "audio/flac"):
        encodingType = speech.RecognitionConfig.AudioEncoding.FLAC
        sampleRateHertz = 48000 # 44100
    else:
        encodingType = speech.RecognitionConfig.AudioEncoding.LINEAR16
        sampleRateHertz = 16000

    audio_content = await file.read()
    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=encodingType,
        sample_rate_hertz=sampleRateHertz,
        language_code=language_code, # "en-US"
    )
    response = client.recognize(config=config, audio=audio)
    transcriptions = [result.alternatives[0].transcript for result in response.results]
    return {"transcriptions": transcriptions}
