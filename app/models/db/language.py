from sqlalchemy import (
    Column,
    Integer,
    String,
)

from app.infrastructure.db.database import Base


class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    language_name = Column(String, nullable=False, unique=True)
