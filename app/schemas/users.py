from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class Auth0User(BaseModel):
    id: str = Field(..., alias='sub')
    permissions: Optional[List[str]]


class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    country: Optional[str]
    language: Optional[str]
    phone_number: Optional[str]
    nickname: Optional[str]
    dob: Optional[date]
