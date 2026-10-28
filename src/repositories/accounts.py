import secrets
from datetime import datetime, timezone, timedelta

from src.repositories.base import AsyncBaseRepository, SyncBaseRepository
from src.database.models.accounts import (
    UserModel,
    UserGroupModel,
    UserProfileModel,
    AbstractTokenModel
)


class UserRepository(AsyncBaseRepository[UserModel]):

    def __init__(self) -> None:
        super().__init__(UserModel)


class UserGroupRepository(AsyncBaseRepository[UserGroupModel]):

    def __init__(self) -> None:
        super().__init__(UserGroupModel)


class TokenRepository(
    AsyncBaseRepository[AbstractTokenModel],
    SyncBaseRepository[AbstractTokenModel]
):

    @staticmethod
    def generate_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def get_expiration_date(td: timedelta = timedelta(days=1)) -> datetime:
        return datetime.now(timezone.utc) + td


class UserProfileRepository(AsyncBaseRepository[UserProfileModel]):

    def __init__(self) -> None:
        super().__init__(UserProfileModel)
