from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[T]:

    def __init__(self, model_type: type[T]) -> None:
        self._model_type = model_type

    async def aget_all(self, db: AsyncSession) -> Sequence[T]:
        result = await db.execute(select(self._model_type))
        return result.scalars().all()

    async def aget_by_id(self, db: AsyncSession, id_: int) -> T | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.id == id_)
        )
        return result.scalar_one_or_none()

    async def acreate(self, db: AsyncSession, data: dict) -> T:
        instance = self._model_type(**data)

        db.add(instance)
        await db.flush()

        return instance

    async def aupdate_by_id(
        self,
        db: AsyncSession,
        id_: int,
        data: dict
    ) -> T | None:
        instance = await self.aget_by_id(db, id_)

        if not instance:
            return None

        for name, value in data.items():
            setattr(instance, name, value)

        await db.flush()
        return instance

    async def adelete_by_id(self, db: AsyncSession, id_: int) -> T | None:
        instance = await self.aget_by_id(db, id_)

        if not instance:
            return instance

        await db.delete(instance)
        return instance

    def get_all(self, db: Session) -> Sequence[T]:
        result = db.execute(select(self._model_type))
        return result.scalars().all()

    def get_by_id(self, db: Session, id_: int) -> T | None:
        result = db.execute(
            select(self._model_type)
            .where(self._model_type.id == id_)
        )
        return result.scalar_one_or_none()

    def create(self, db: Session, data: dict) -> T:
        instance = self._model_type(**data)

        db.add(instance)
        db.flush()

        return instance

    def update_by_id(self, db: Session, id_: int, data: dict) -> T | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        return instance

    def delete_by_id(self, db: Session, id_: int) -> T | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        db.delete(instance)
        return instance
