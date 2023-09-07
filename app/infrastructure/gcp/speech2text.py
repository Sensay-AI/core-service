import base64
import json
import os
import tempfile

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech


class Speech2Text:
    def __init__(
        self,
        encoded_credentials: str,
        recogniser_gcp: str,
        config: cloud_speech.RecognitionConfig,
    ):
        decoded_credentials = base64.b64decode(
            encoded_credentials.encode("utf-8")
        ).decode("utf-8")
        credentials_dict = json.loads(decoded_credentials)

        # Create a temporary file and write the credentials dictionary to it
        temp_fd, temp_credentials_file = tempfile.mkstemp()
        with open(temp_credentials_file, "w") as f:
            json.dump(credentials_dict, f)

        # Initialize the SpeechClient using the temporary credentials file
        self.client = SpeechClient.from_service_account_file(temp_credentials_file)

        # init config to inject
        self.config = config
        self.recogniser_gcp = recogniser_gcp

        # Clean up: Close the file descriptor and remove the temporary file
        os.close(temp_fd)
        os.remove(temp_credentials_file)

    def transcribe_audio(self, audio_content: bytes) -> str:
        request = cloud_speech.RecognizeRequest(
            recognizer=self.recogniser_gcp,
            config=self.config,
            content=audio_content,
        )

        response = self.client.recognize(request=request)
        transcriptions = [
            result.alternatives[0].transcript for result in response.results
        ]

        response_transcribe = "".join(transcriptions)
        return response_transcribe
