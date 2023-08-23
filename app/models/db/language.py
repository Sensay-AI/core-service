from sqlalchemy import Column, DateTime, Integer, String, func

from app.infrastructure.db.database import Base


class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    language_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
