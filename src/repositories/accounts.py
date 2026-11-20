import secrets
from datetime import datetime, timezone, timedelta

from src.repositories.base import AsyncBaseRepository, SyncBaseRepository
from src.database.models import accounts as models


class UserRepository(AsyncBaseRepository[models.UserModel]):

    def __init__(self) -> None:
        super().__init__(models.UserModel)


class UserGroupRepository(AsyncBaseRepository[models.UserGroupModel]):

    def __init__(self) -> None:
        super().__init__(models.UserGroupModel)


class TokenRepository(
    AsyncBaseRepository[models.AbstractTokenModel],
    SyncBaseRepository[models.AbstractTokenModel]
):

    @staticmethod
    def generate_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def get_expiration_date(td: timedelta = timedelta(days=1)) -> datetime:
        return datetime.now(timezone.utc) + td


class UserProfileRepository(AsyncBaseRepository[models.UserProfileModel]):

    def __init__(self) -> None:
        super().__init__(models.UserProfileModel)
