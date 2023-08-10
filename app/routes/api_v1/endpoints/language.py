from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth0 import check_user
from app.crud.base import CRUDBase
from app.db.database import get_db
from app.models.language import Language

router = APIRouter()


@router.get("/")
async def get_supported_languages(
    *, db: Session = Depends(get_db), _: Any = Depends(check_user)
) -> dict[str, list[dict]]:
    model: CRUDBase = CRUDBase(Language)
    supported_languages: list[Language] = model.get_multi(db)
    result = [x.__dict__ for x in supported_languages]
    return {"items": result}
