from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncBaseRepository[T]:

    def __init__(self, model_type: type[T]) -> None:
        self._model_type = model_type

    async def aget_all(self, db: AsyncSession) -> Sequence[T]:
        result = await db.execute(select(self._model_type))
        return result.scalars().all()

    async def aget_by_ids(self, db: AsyncSession, ids: list[int]) -> Sequence[T]:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.id.in_(ids))
        )
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

    @staticmethod
    async def aupdate(db: AsyncSession, instance: T, data: dict) -> None:
        for name, value in data.items():
            setattr(instance, name, value)

        await db.flush()

    async def aupdate_by_id(
        self,
        db: AsyncSession,
        id_: int,
        data: dict
    ) -> T | None:
        instance = await self.aget_by_id(db, id_)

        if not instance:
            return None

        await self.aupdate(db, instance, data)
        return instance

    async def adelete_by_id(self, db: AsyncSession, id_: int) -> T | None:
        instance = await self.aget_by_id(db, id_)

        if not instance:
            return instance

        await db.delete(instance)
        return instance

    @staticmethod
    async def adelete(db: AsyncSession, instance: T) -> None:
        await db.delete(instance)


class SyncBaseRepository[T]:

    def __init__(self, model_type: type[T]) -> None:
        self._model_type = model_type

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

    @staticmethod
    def update(db: Session, instance: T, data: dict) -> None:
        for name, value in data.items():
            setattr(instance, name, value)

        db.flush()

    def update_by_id(self, db: Session, id_: int, data: dict) -> T | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        self.update(db, instance, data)
        return instance

    def delete_by_id(self, db: Session, id_: int) -> T | None:
        instance = self.get_by_id(db, id_)

        if not instance:
            return None

        db.delete(instance)
        return instance

    @staticmethod
    def delete(db: Session, instance: T) -> None:
        db.delete(instance)
