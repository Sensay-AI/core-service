from pydantic import BaseModel, Field


class ImageCaptionRequest(BaseModel):
    image_url: str = Field(description="image url to generation captions from")
    learning_language: str = Field(description="languages to generate caption in")
    primary_language: str = Field(description="original language")
