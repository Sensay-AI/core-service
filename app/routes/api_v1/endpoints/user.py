from __future__ import annotations

from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth0 import check_user
from app.db.database import get_db
from app.models.users import UserInfo
from app.schemas.users import Auth0User, UserUpdate

router = APIRouter()


@router.get("/")
async def get_user_profile(
    *, db: Session = Depends(get_db), auth: Auth0User = Depends(check_user)
) -> dict[str, Any]:
    user: Optional[UserInfo] = (
        db.query(UserInfo).filter(UserInfo.user_id == auth.id).first()
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user does not exists!",
        )
    return user.__dict__


@router.post("/create")
async def create_user_profile(
    *,
    user_input: UserUpdate,
    db: Session = Depends(get_db),
    auth: Auth0User = Depends(check_user),
) -> dict[str, str]:
    user: Optional[UserInfo] = (
        db.query(UserInfo).filter(UserInfo.user_id == auth.id).first()
    )

    if user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user already exists!",
        )
    try:
        user = UserInfo()
        user.user_id = auth.id
        user.full_name = user_input.full_name
        user.email = user_input.email
        user.country = user_input.country
        user.language = user_input.language
        user.phone_number = user_input.phone_number
        user.nickname = user_input.nickname
        user.date_of_birth = user_input.date_of_birth
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Create user successfully!"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.__str__()
        )


@router.put("/update")
async def update_user_profile(
    *,
    user_input: UserUpdate,
    db: Session = Depends(get_db),
    auth: Auth0User = Depends(check_user),
) -> dict[str, str]:
    user: Optional[UserInfo] = (
        db.query(UserInfo).filter(UserInfo.user_id == auth.id).first()
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="The user does not exists!",
        )
    try:
        user.full_name = user_input.full_name
        user.email = user_input.email
        user.country = user_input.country
        user.language = user_input.language
        user.phone_number = user_input.phone_number
        user.nickname = user_input.nickname
        user.date_of_birth = user_input.date_of_birth

        db.commit()
        db.refresh(user)
        return {"message": "Update user successfully!"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.__str__()
        )
