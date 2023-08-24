from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.models.common.pagination import PageParams
from app.models.db.language import Language
from app.routes.api_v1.endpoints.auth import check_user
from app.services.base_service import BaseService

router = APIRouter()


@router.get("/")
@inject
async def get_supported_languages(
    *,
    page_params: PageParams = Depends(),
    language_service: BaseService = Depends(Provide[Container.language_service]),
    _: Any = Depends(check_user),
) -> object:
    return language_service.get_multi(
        page=page_params.page, size=page_params.size, sort_by=Language.created_at.desc()
    )
