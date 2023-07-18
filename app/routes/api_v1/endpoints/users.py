from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.orm import Session
from http import HTTPStatus
from app.db.database import get_db
from app.models.users import UserInfo
from app.schemas.users import UserCreate
from app.core.security import get_password_hash
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import or_

router = APIRouter()


@router.get("/")
async def get_all_users(
        *,
        db: Session = Depends(get_db),
        # auth: Depends = Depends(get_current_user),
) -> dict[str, Any]:
    users = db.query(UserInfo).all()
    return {
        "items": users
    }


@router.post("/sign_up")
async def create_user(
        *,
        user_input: UserCreate,
        db: Session = Depends(get_db),
        # auth: Depends = Depends(get_current_user),
) -> dict[str, str]:
    user: Optional[UserInfo] = db.query(UserInfo).filter(
        or_(UserInfo.email == user_input.email, UserInfo.phone_number == user_input.phone_number)
    ).first()

    if user:
        if user.phone_number:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="The user with this phone number already exists in the system.",
            )
        if user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="The user with this email already exists in the system.",
            )

    user = UserInfo(
        full_name=user_input.full_name,
        email=user_input.email,
        # password=get_password_hash(user_input.password),
        password=user_input.password,
        phone_number=user_input.phone_number,
        dob=user_input.dob
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Create successfully!"
    }
