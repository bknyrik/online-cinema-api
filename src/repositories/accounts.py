from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.services.security import PasswordSecurityService
from src.repositories.base import BaseRepository
from src.database.models.accounts import UserModel


class UserRepository(BaseRepository):

    def __init__(self, pss: PasswordSecurityService) -> None:
        super().__init__(UserModel)
        self._pss = pss

    async def aget_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.email == email)
        )
        return result.scalar_one_or_none()

    def get_by_email(self, db: Session, email: str) -> UserModel | None:
        result = db.execute(
            select(self._model_type)
            .where(self._model_type.email == email)
        )
        return result.scalar_one_or_none()

    async def acreate(self, db: AsyncSession, data: dict) -> UserModel:
        password = self._pss.hash_password(data.pop("password"))
        user = self._model_type(**data, hashed_password=password)

        db.add(user)
        await db.flush()

        return user

    async def aupdate_by_id(
        self,
        db: Session,
        id_: int,
        data: dict
    ) -> UserModel | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        instance.email = data.get("email", instance.email)
        instance.group_id = data.get("group_id", instance.group_id)
        instance.is_active = data.get("is_active", instance.is_active)

        if data.get("password"):
            instance.hashed_password = self._pss.hash_password(
                data["password"]
            )

        if data:
            instance.updated_at = datetime.now(timezone.utc)

        await db.flush()
        return instance

    def create(self, db: AsyncSession, data: dict) -> UserModel:
        password = self._pss.hash_password(data.pop("password"))
        user = self._model_type(**data, hashed_password=password)

        db.add(user)
        db.flush()

        return user

    def update_by_id(
        self,
        db: Session,
        id_: int,
        data: dict
    ) -> UserModel | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        instance.email = data.get("email", instance.email)
        instance.group_id = data.get("group_id", instance.group_id)
        instance.is_active = data.get("is_active", instance.is_active)

        if data.get("password"):
            instance.hashed_password = self._pss.hash_password(
                data["password"]
            )

        if data:
            instance.updated_at = datetime.now(timezone.utc)

        db.flush()
        return instance
