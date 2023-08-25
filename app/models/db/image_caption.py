from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.db.database import Base

FOREIGN_LANGUAGE_ID = "languages.id"


class ImageCaption(Base):
    __tablename__ = "image_caption"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)
    image_bucket_path_key = Column(String, nullable=False)
    language_id = Column(Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False)
    language = relationship("Language")
    caption = Column(String, nullable=False)
    translations = relationship("ImageCaptionTranslation", back_populates="caption")
    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), server_default=func.now())


class ImageCaptionTranslation(Base):
    __tablename__ = "image_captions_translations"
    id = Column(Integer, primary_key=True)
    translated_caption = Column(String)
    caption_id = Column(Integer, ForeignKey("image_caption.id"), nullable=False)
    caption = relationship("ImageCaption", back_populates="translations")
    translated_language = relationship("Language")
    translated_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
