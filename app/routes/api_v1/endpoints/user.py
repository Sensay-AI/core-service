import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.container.containers import Container
from app.models.db.users import UserInfo
from app.models.schemas.users import Auth0User, UserUpdate
from app.repositories.user_repository import NotFoundError, NotUniqueError
from app.routes.api_v1.endpoints.auth import check_user
from app.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger()


@router.get("/")
@inject
async def get_user_profile(
    *,
    user_service: UserService = Depends(Provide[Container.user_service]),
    auth: Auth0User = Depends(check_user),
) -> object:
    try:
        return user_service.get_user_by_id(auth.id)
    except NotFoundError:
        return Response(
            "User not found or maybe new user", status_code=status.HTTP_404_NOT_FOUND
        )


@router.post("/create")
@inject
def create_user_profile(
    user_input: UserUpdate,
    user_service: UserService = Depends(Provide[Container.user_service]),
    auth: Auth0User = Depends(check_user),
) -> object:
    logger.debug(f"Start create_user_profile with input: {user_input}")
    try:
        return user_service.create_user(user_info_from(auth, user_input))
    except NotUniqueError as e:
        return HTTPException(status_code=10001, detail=e.__str__())


@router.put("/update")
@inject
def update_user_profile(
    user_input: UserUpdate,
    user_service: UserService = Depends(Provide[Container.user_service]),
    auth: Auth0User = Depends(check_user),
) -> object:
    try:
        return user_service.update_user(user_info_from(auth, user_input))
    except NotUniqueError as e:
        return HTTPException(status_code=10001, detail=e.__str__())


def user_info_from(auth: Auth0User, user_input: UserUpdate) -> UserInfo:
    return UserInfo(
        user_id=auth.id,
        full_name=user_input.full_name,
        email=user_input.email,
        country=user_input.country,
        language=user_input.language,
        phone_number=user_input.phone_number,
        nickname=user_input.nickname,
        date_of_birth=user_input.date_of_birth,
        gender="" if user_input.gender is None else user_input.gender.name,
        picture=user_input.picture,
    )
