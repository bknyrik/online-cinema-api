import secrets
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select

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

    async def aget_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.email == email)
        )
        return result.scalar_one_or_none()


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

    async def aget_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> AbstractTokenModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def aupdate_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        data: dict
    ) -> AbstractTokenModel | None:
        instance = await self.aget_by_user_id(db, user_id)

        if not instance:
            return None

        await self.aupdate(db, instance, data)
        return instance


class UserProfileRepository(AsyncBaseRepository[UserProfileModel]):

    def __init__(self) -> None:
        super().__init__(UserProfileModel)
