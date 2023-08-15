import logging
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.infrastructure.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        session_factory: Callable[..., AbstractContextManager[Session]],
    ):
        self.model = model
        self.session_factory = session_factory
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get(self, id: Any) -> Optional[ModelType]:
        with self.session_factory() as session:
            try:
                return session.query(self.model).filter(self.model.id == id).first()
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def query(self, query: Any, limit: int = 200) -> Optional[ModelType]:
        with self.session_factory() as session:
            try:
                return session.query(self.model).filter(query).limit(limit).all()
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        with self.session_factory() as session:
            try:
                return session.query(self.model).offset(skip).limit(limit).all()
            except SQLAlchemyError as err:
                self.logger.error(err)
            return []

    def create(
        self, *, obj_in: CreateSchemaType, commit: bool = True
    ) -> Optional[ModelType]:
        with self.session_factory() as session:
            try:
                obj_in_data = jsonable_encoder(obj_in)
                db_obj = self.model(**obj_in_data)
                session.add(db_obj)
                if commit:
                    session.commit()
                    session.refresh(db_obj)
                return db_obj
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> Optional[ModelType]:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        with self.session_factory() as session:
            try:
                session.add(db_obj)
                if commit:
                    session.commit()
                    session.refresh(db_obj)
                return db_obj
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def remove(self, *, id: int, commit: bool = True) -> Optional[ModelType]:
        with self.session_factory() as session:
            try:
                obj = session.query(self.model).get(id)
                session.delete(obj)
                if commit:
                    session.commit()
                return obj
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None
