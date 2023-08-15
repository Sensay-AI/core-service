from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.container.containers import Container
from app.models.language import Language
from app.repositories.base_repository import BaseRepository
from app.routes.api_v1.endpoints.auth import check_user

router = APIRouter()


@router.get("/")
@inject
async def get_supported_languages(
    *,
    repo: BaseRepository = Depends(Provide[Container.language_repository]),
    _: Any = Depends(check_user),
) -> dict[str, list[dict]]:
    supported_languages: list[Language] = repo.get_multi()
    result = [x.__dict__ for x in supported_languages]
    return {"items": result}
