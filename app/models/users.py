from sqlalchemy import *
from app.db.database import Base
import enum


class Gender(enum.Enum):
    female = 0
    male = 1
    other = 2


class UserInfo(Base):
    __tablename__ = 'users_info'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=false)
    email = Column(String, nullable=false, unique=true)
    password = Column(String, nullable=false)
    phone_number = Column(String(20), nullable=false, unique=true)
    gender = Column(Enum(Gender), default=Gender.other)
    dob = Column(Date)
    created_at = Column(DateTime(timezone=true), server_default=func.now())
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)



