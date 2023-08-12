import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.container.containers import Container
from app.infrastructure.auth0.auth0 import Auth0Service
from app.schemas.users import Auth0User

logger = logging.getLogger()
router = APIRouter()


@router.post("/")
@inject
def check_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: Auth0Service = Depends(Provide[Container.auth]),
) -> Auth0User:
    return auth_service.verify_token(token.credentials)
