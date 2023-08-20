from typing import Any, Dict, Optional, Union

from app.infrastructure.pagination import PagedResponseSchema
from app.repositories.base_repository import (
    BaseRepository,
    CreateSchemaType,
    ModelType,
    UpdateSchemaType,
)


class BaseService:
    def __init__(
        self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
    ) -> None:
        self._repository = repository

    def get(self, model_id: Any) -> PagedResponseSchema[ModelType]:
        return self._repository.get(model_id)

    def query(self, query: Any, page: int, size: int) -> PagedResponseSchema[ModelType]:
        return self._repository.query(query=query, page=page, size=size)

    def get_multi(self, page: int, size: int) -> PagedResponseSchema[ModelType]:
        return self._repository.get_multi(page=page, size=size)

    def create(
        self, obj_in: CreateSchemaType, commit: bool = True
    ) -> Optional[ModelType]:
        return self._repository.create(obj_in=obj_in, commit=commit)

    def update(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> Optional[ModelType]:
        return self._repository.update(db_obj=db_obj, obj_in=obj_in, commit=commit)

    def remove(self, model_id: int, commit: bool = True) -> Optional[ModelType]:
        return self._repository.remove(id=model_id, commit=commit)
