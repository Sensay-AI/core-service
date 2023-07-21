from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.orm import Session
from http import HTTPStatus
from app.db.database import get_db
from app.models.users import UserInfo
from app.schemas.users import UserUpdate, Auth0User
from fastapi import APIRouter, Body, Depends, HTTPException
from app.core.auth0 import check_user

router = APIRouter()


@router.get("/")
async def get_user_profile(
        *,
        auth: Auth0User = Depends(check_user)
):
    return auth


@router.post("/create")
async def create_user_profile(
        *,
        user_input: UserUpdate,
        db: Session = Depends(get_db),
        auth: Auth0User = Depends(check_user)
) -> dict[str, str]:
    user: Optional[UserInfo] = db.query(UserInfo).filter(
        UserInfo.user_id == auth.id
    ).first()

    if user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user already exists!",
        )

    user = UserInfo()
    user.user_id = auth.id
    user.full_name = user_input.full_name
    user.email = user_input.email
    user.country = user_input.country
    user.language = user_input.language
    user.phone_number = user_input.phone_number
    user.nickname = user_input.nickname
    user.dob = user_input.dob
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Create user successfully!"
    }

@router.put("/update")
async def update_user_profile(
        *,
        user_input: UserUpdate,
        db: Session = Depends(get_db),
        auth: Auth0User = Depends(check_user)
) -> dict[str, str]:
    user: Optional[UserInfo] = db.query(UserInfo).filter(
        UserInfo.user_id == auth.id
    ).first()

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user does not exists!",
        )

    user.full_name = user_input.full_name
    user.email = user_input.email
    user.country = user_input.country
    user.language = user_input.language
    user.phone_number = user_input.phone_number
    user.nickname = user_input.nickname
    user.dob = user_input.dob
    db.commit()
    db.refresh(user)

    return {
        "message": "Update user successfully!"
    }
