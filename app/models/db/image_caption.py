from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.infrastructure.db.database import Base


class ImageCaption(Base):
    __tablename__ = "image_caption"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)
    image_url = Column(Integer)
    caption_learning_language = Column(String)
    caption_primary_language = Column(String)
    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), server_default=func.now())
