from sqlalchemy import *
from app.db.database import Base
import enum


class Gender(enum.Enum):
    female = 0
    male = 1
    other = 2


class UserInfo(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=true, nullable=false)
    full_name = Column(String, nullable=false)
    nickname = Column(String)
    email = Column(String, nullable=false, unique=true)
    phone_number = Column(String(20), nullable=false, unique=true)
    gender = Column(Enum(Gender), default=Gender.other)
    country = Column(String(20),default="VietNam")
    language = Column(String(20),default="VietNam")
    dob = Column(Date)
    picture = Column(String)
    created_at = Column(DateTime(timezone=true), server_default=func.now())
    updated_at = Column(DateTime(timezone=true), server_default=func.now())



