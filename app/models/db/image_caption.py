from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.db.database import Base

FOREIGN_LANGUAGE_ID = "languages.id"


class ImageCaptionPrimaryLanguage(Base):
    __tablename__ = "image_caption"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)
    image_bucket_path_key = Column(String, nullable=False)
    primary_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
    primary_language = relationship("Language")
    caption = Column(String, nullable=False)
    learning_caption = relationship(
        "ImageCaptionLearningLanguage", back_populates="caption"
    )
    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), server_default=func.now())


class ImageCaptionLearningLanguage(Base):
    __tablename__ = "image_caption_translation"
    id = Column(Integer, primary_key=True)
    learning_language_caption = Column(String)
    caption_id = Column(Integer, ForeignKey("image_caption.id"), nullable=False)
    caption = relationship(
        "ImageCaptionPrimaryLanguage", back_populates="learning_caption"
    )
    learning_language = relationship("Language")
    learning_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
