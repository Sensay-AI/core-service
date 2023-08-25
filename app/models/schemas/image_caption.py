from pydantic import BaseModel, Field


class ImageCaptionRequest(BaseModel):
    image_bucket_path_key: str = Field(
        description="image bucket path key to generation captions from"
    )
    learning_language: str = Field(description="languages to generate caption in")
    primary_language: str = Field(description="original language")


class ImageCaptionCreate(BaseModel):
    image_path: str
    caption: str
    translation: str
    primary_language: str
    learning_language: str
