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
encoded_credentials = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicGh1bmctc2Vuc2F5LWFpLXNwZWVjaDJ0ZXh0IiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiN2NhM2JjMGJlN2UwNGE2NTJlMTk2YTNkZGQ3N2EwOGEwZThjODA0OSIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZBSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS1l3Z2dTaUFnRUFBb0lCQVFEUVAwQWZ5eHFneWlIL1xud0kzdndKN09zWXBSUUJjYktWOXpDTThqcG5sR2VJMnh2bHNjRVZHTEVMcmIvWEUrUk1ReG1ZWDZwMUhoZkIwWlxuRTNjclMrN0U2SEpBRVNHZno5TVo4YVVEZElHM0w3cDdaQjRwSHJEUUJTVjc4b3RjNjlDa0V2V0pGK0lRT2xYZlxuMmoySnJrRVRMcWFUeW1tdE5OL2ZoUEVWR0JDVk01Si9mckZJMTlLMXQ4S1BGQ0dzcnB0VHNTUEhGMk9DbjRhZlxuaWlhWVFDL1gyOXRQRDR5RUltMGNKem9aMjd3YU5XclczMGo5elNBb1d0TUwvSmFRdkF1VUtGMlI4Z1U4cWNrTlxua0FFeW5RNzNaNlJvaVY4UUFERlg3UmhTSGVwZVVTZ282a1dkL2dwTlNqK2ErazVReUtPYlNlekcxeERVR1g3UFxuaWR2YnZFMmhBZ01CQUFFQ2dnRUFNZ21rcTQ4R3FyQnZDM0ExMnJBMnFIVWVCbWhuTk9wVHlrVUpXcWhYVnlERFxuOFR2TFVocnlORDlVbXVRU3lCTEhicUNVUWhaZXRSYTR1aXdFZENXV2JYOXA1bTJIWGdwV2o5TVJvcHNseVFIQlxucGdENFEwcWgweFlOZS9NYlcvdzRvWmdCb2d1WVVPeG5jbmFTMTBpRXorcGpjYnNPK2VTc3oxMDIvV25QSUQ0NVxuTWFBNHJtbk5td2d4RktWUHBEa21rWmN3b0s2Y0g3a2IxMW9yWklBcndsMjgzdzA3azNsVW5xSzhaYkpkRUVJUFxuV0ExRVpBR0ZJNFlpQlpmdlp4bVVXTk5sbUVDQVdkVG5mZ2trOGg2Y2FTREQ3c0M0TnNRTDdob29ZTWs0bVZVSlxuMmk3c3EwWGxRVWdNbThMazBUd2laUlRxMFJZMzlKWjNVUGI5R1ZVTHZRS0JnUUQxUXBWelJqTmRpcFJHWU9DNlxuSlc0NlV4bWVRelNFM1puZisvODFNckF5RDF0YURZblFKaGtsZ2MwOFNKWTNJN0hPcWJ2VXd4aWFrb2RuQ2Y2c1xubUlkdnNIQ2RZT1pYeW83NW5tUU1SM0NBblN0ZWF5eURXYXFVVjZrSml4UXJZa1cwK0k1VDdyMlQ5NmZVL2xjWlxud0JsZ25FeUdUTHl4allUMzJIaDl3TStZalFLQmdRRFpYYjQ3NGU4WXNMWSs0ZnlReG4xaHhEcnZlN0p4bnYyM1xuY04yMDJYd1NrU0twcGo5MXFjSUdTN3RkZWtrSDIxR0tvQktDNUlBMms1THVMejVObTJFaUZUYzk4cUJFWW4rRVxuRkxSVTBESG9ldnRmQlZTRTRIS1FQOHpTanlNdWdtck5Ieng2Tkw1WG9YSjZGMmVpa3FrZFVVQ1pkbG5uTUpnWVxuM2ZSSmhkMFdaUUtCZ0NmejlNeVdmditaOTVXUGFveG9WSkNEd1FTYkJnOHUya1kya3RoanJYZzZNRE4zU1IvelxuVk4xYlM4ZXFPMjQ0RGxzUUkxMEJleHlUQ2lPcTZTWE1veU42cHAyOGowbDE0ZHlnQk1STFR2UmtwZy8zZllUWVxuTW9WLzBqV1B4blZheU9nMkpWbGU1dHNYMk90Rms0TEtYRmYwbmpLeWhYcVhCellvdVZnaTlLNXhBb0dBVldsWVxuanY5QWpGc2p3YUhiTktoS0xGaUhNQU5USXdKdWY5NkJ2OGFWMGxYbFlQUktpMW1oUEFnV0g2MGxkVWpneWJBTVxubGhKanJ3NWQ5ZW5xZVdSTXpxKzNmVWdSWWMyeWZad0ZJQzZPN2VNbFV6a3M5T21kR3NGM0ltWE1WVUk1NVZBWVxuMjR4T0h2RDVvcS8vc1FvZ0diMEx2VUdjSWhRZUwrZEhUbnlqVzJFQ2dZQUdySnlqUUNHOEpFRTVIck12ZHdsT1xuTktOa3NZbUozbFZERnpzY0NGMENneE9zd1hiNGtCVTRMTmJIRmFUOXFJcVZUQVhsUVRVRmVxamMveE40TnhpK1xuV3pMZXdQNXNWQ1FBMGdXYXZMclYrTWRFby8xNmFUby81bTZOK3FnS2dOQWV1dlBZN2UrbEpMa09NR09hOTlXR1xuMmFhM1FzWjdmZTdWL1M2WU1YL09pdz09XG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAic2Vuc2F5LWFpLXRlc3RAcGh1bmctc2Vuc2F5LWFpLXNwZWVjaDJ0ZXh0LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwMDAzODU3MTgzOTU0MzEyNTU1MSIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvc2Vuc2F5LWFpLXRlc3QlNDBwaHVuZy1zZW5zYXktYWktc3BlZWNoMnRleHQuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0="
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
