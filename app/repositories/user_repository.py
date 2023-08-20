import logging
from contextlib import AbstractContextManager
from typing import Callable, Iterator, Optional

from psycopg2 import errors
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.db.users import UserInfo

UniqueViolation = errors.lookup("23505")  # Correct way to Import the psycopg2 errors


class UserRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )

    def get_all(self) -> Iterator[UserInfo]:
        with self.session_factory() as session:
            return session.query(UserInfo).all()

    def get_by_id(self, user_id: str) -> UserInfo:
        with self.session_factory() as session:
            user = session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
            if not user:
                raise UserNotFoundError(user_id)
            return user

    def add(self, user_info: UserInfo) -> UserInfo | None:
        with self.session_factory() as session:
            try:
                session.add(user_info)
                session.commit()
                session.refresh(user_info)
                return user_info
            except IntegrityError as err:
                self.logger.error(err)
                if isinstance(err.orig, UniqueViolation):
                    raise NotUniqueError(err.orig.pgcode, err.orig.pgerror)
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def update(self, user_info: UserInfo) -> UserInfo | None:
        with self.session_factory() as session:
            try:
                user: Optional[UserInfo] = (
                    session.query(UserInfo)
                    .filter(UserInfo.user_id == user_info.user_id)
                    .first()
                )
                if user is not None:
                    user.full_name = user_info.full_name
                    user.email = user_info.email
                    user.country = user_info.country
                    user.language = user_info.language
                    user.phone_number = user_info.phone_number
                    user.nickname = user_info.nickname
                    user.date_of_birth = user_info.date_of_birth
                    user.gender = user_info.gender
                    user.picture = user_info.picture
                    session.commit()
                    session.refresh(user)
                return user
            except IntegrityError as err:
                self.logger.error(err)
                if isinstance(err.orig, UniqueViolation):
                    raise NotUniqueError(err.orig.pgcode, err.orig.pgerror)
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None

    def delete_by_id(self, user_id: str) -> None:
        with self.session_factory() as session:
            entity: UserInfo = (
                session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
            )
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id: str):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"


class NotUniqueError(Exception):
    def __init__(self, pg_code: str, pg_error: str):
        super().__init__(f" DB error_code: {pg_code} DB error_msg: {pg_error}")
