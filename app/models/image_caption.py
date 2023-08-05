from enum import auto
from pydantic import constr, validator
from fastapi_utils.enums import StrEnum
from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList


from app.core import config
from app.db.database import Base, init_db

from pydantic import BaseModel, Field


SUPPORTED_LANGUAGES = config.SUPPORTED_LANGUAGES.split(',')


def validate_language_in_list(language: str) -> str:
    if language.lower() not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language. \
                         Available languages: {', '.join(SUPPORTED_LANGUAGES)}")
    return language


class Language(StrEnum):
    english = auto()
    vietnamse = auto()


class ImageCaptionRequest(BaseModel):
    user_id: str = Field(
        default="",
        description="user id for saving history for further analysis"
    )
    image_url: str = Field(description="image url to generation captions from")
    language: constr(strip_whitespace=True)
    @validator('language')
    def validate_language(cls, language):
        return validate_language_in_list(language)


class UserImage(Base):
    __tablename__ = "user_images"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    captioned_images = Column(MutableList.as_mutable(ARRAY(JSONB)))
