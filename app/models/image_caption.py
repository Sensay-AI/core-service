from enum import auto
<<<<<<< HEAD

from fastapi_utils.enums import StrEnum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core import config
from app.db.database import Base

SUPPORTED_LANGUAGES = config.SUPPORTED_LANGUAGES.split(",")


def validate_language_in_list(language: str) -> str:
    if language.lower() not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language. Available languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )
=======
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
        raise ValueError(f"Unsupported language. Available languages: {', '.join(SUPPORTED_LANGUAGES)}")
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
    return language


class Language(StrEnum):
    english = auto()
<<<<<<< HEAD
    vietnamese = auto()
    spanish = auto()
    japanese = auto()
=======
    vietnamse = auto()
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)


class ImageCaptionRequest(BaseModel):
    user_id: str = Field(
<<<<<<< HEAD
        default="", description="user id for saving history for further analysis"
    )
    image_url: str = Field(description="image url to generation captions from")
    language: str = Field(description="languages to generate caption in")

    @validator("language")
    def validate_language(cls, language: str) -> str:
        return validate_language_in_list(language)


class ImageCaption(Base):
    __tablename__ = "image_caption"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)
    image_url = Column(Integer)
    caption = Column(String)
    language = Column(String)
    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), server_default=func.now())
=======
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

init_db()
>>>>>>> 90f0aa9 (implemen image captioning SAI-27)
