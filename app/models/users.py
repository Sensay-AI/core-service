import enum

from sqlalchemy import Column, Date, DateTime, Enum, Integer, String, func

from app.db.database import Base


class Gender(enum.Enum):
    female = 0
    male = 1
    other = 2
    prefer_not_to_say = 3


class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    nickname = Column(String)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    gender = Column(String(20), default=Gender.other.name)
    country = Column(String, default="")
    language = Column(String, default="")
    date_of_birth = Column(Date)
    picture = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
