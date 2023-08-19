from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.models.language import Language
from app.routes.api_v1.endpoints.auth import check_user
from app.services.base_service import BaseService

router = APIRouter()


@router.get("/")
@inject
async def get_supported_languages(
    *,
    language_service: BaseService = Depends(Provide[Container.language_service]),
    _: Any = Depends(check_user),
) -> dict[str, list[dict]]:
    supported_languages: list[Language] = language_service.get_multi()
    result = [x.__dict__ for x in supported_languages]
    return {"items": result}
