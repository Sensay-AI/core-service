from typing import Optional
from pydantic import BaseModel
from datetime import date


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone_number: str
    dob: Optional[date]
