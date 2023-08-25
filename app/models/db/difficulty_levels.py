from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    func,
)

from app.infrastructure.db.database import Base


class DifficultyLevels(Base):
    __tablename__ = "difficulty_levels"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
