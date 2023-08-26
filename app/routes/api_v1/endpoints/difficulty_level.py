from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.models.common.pagination import PageParams
from app.models.db.difficulty_levels import DifficultyLevels
from app.routes.api_v1.endpoints.auth import check_user
from app.services.base_service import BaseService

router = APIRouter()


@router.get("/")
@inject
async def get_all_difficulty_lesson_level(
    *,
    page_params: PageParams = Depends(),
    difficulty_levels: BaseService = Depends(
        Provide[Container.difficulty_levels_service]
    ),
    _: Any = Depends(check_user),
) -> object:
    return difficulty_levels.get_multi(
        page=page_params.page,
        size=page_params.size,
        sort_by=DifficultyLevels.created_at.desc(),
    )
