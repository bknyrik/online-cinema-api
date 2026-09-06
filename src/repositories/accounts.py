import secrets
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.database.models.accounts import (
    UserModel,
    UserGroupModel,
    AbstractTokenModel
)


class UserRepository(BaseRepository[UserModel]):

    def __init__(self) -> None:
        super().__init__(UserModel)

    async def aget_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.email == email)
        )
        return result.scalar_one_or_none()

    async def aget_with_group_by_id(
        self,
        db: AsyncSession,
        id_: int
    ) -> UserModel | None:
        result = await db.execute(
            select(self._model_type)
            .options(joinedload(self._model_type.group))
            .where(self._model_type.id == id_)
        )
        return result.scalar_one_or_none()


class UserGroupRepository(BaseRepository[UserGroupModel]):

    def __init__(self) -> None:
        super().__init__(UserGroupModel)

    async def aget_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> UserGroupModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.name == name)
        )
        return result.scalar_one_or_none()


class TokenRepository(BaseRepository[AbstractTokenModel]):

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

    async def acreate(
        self,
        db: AsyncSession,
        data: dict
    ) -> AbstractTokenModel:
        expires_at = data.get(
            "expires_at",
            self.get_expiration_date()
        )
        token = data.get(
            "token",
            self.generate_token()
        )
        user_id = data["user_id"]
        instance = self._model_type(
            expires_at=expires_at,
            token=token,
            user_id=user_id
        )

        db.add(instance)
        await db.flush()
        return instance

    async def aupdate_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        **data
    ) -> AbstractTokenModel | None:
        instance = await self.aget_by_user_id(db, user_id)

        if not instance:
            return None

        instance.expires_at = data.get(
            "expires_at",
            self.get_expiration_date()
        )
        instance.token = data.get(
            "token",
            self.generate_token()
        )

        await db.flush()

        return instance

    async def adelete_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> AbstractTokenModel | None:
        instance = await self.aget_by_user_id(
            db=db,
            user_id=user_id
        )

        return await self.adelete_by_id(db=db, id_=instance.id)
