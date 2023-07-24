from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Auth0User(BaseModel):
    id: str = Field(..., alias="sub")
    permissions: Optional[List[str]]


class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    country: Optional[str]
    language: Optional[str]
    phone_number: Optional[str]
    nickname: Optional[str]
    date_of_birth: Optional[date]
