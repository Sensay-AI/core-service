from app.models.db.users import UserInfo
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_user_by_id(self, user_id: str) -> UserInfo:
        return self._repository.get_by_id(user_id)

    def create_user(self, user_info: UserInfo) -> UserInfo | None:
        return self._repository.add(user_info)

    def update_user(self, user_info: UserInfo) -> UserInfo | None:
        return self._repository.update(user_info)
