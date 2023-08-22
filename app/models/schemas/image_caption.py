from io import BytesIO
from pydantic import BaseModel, Field


class CaptionInput(BaseModel):
    image_file: BytesIO
    image_path: str


class ImageCaptionRequest(BaseModel):
    image_url: str = Field(description="image url to generation captions from")
    language: str = Field(description="languages to generate caption in")
