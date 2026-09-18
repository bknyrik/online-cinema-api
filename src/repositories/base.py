from typing import Sequence, Literal

from sqlalchemy import select, func, Table, Row
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncBaseRepository[T]:

    def __init__(self, model_type: type[T]) -> None:
        self._model_type = model_type

    async def acount(self, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count()).select_from(self._model_type)
        )
        return result.scalar_one()

    async def aget_all(
        self,
        db: AsyncSession,
        select_columns: list | None = None,
        join_params: list[dict] | None = None,
        offset: int | None = None,
        limit: int | None = None,
        join_relationships: list[str] | None = None,
        expressions: list[ColumnElement[bool]] | None = None,
        order_by_columns: list[ColumnElement[T]] | None = None,
    ) -> Sequence[T]:
        if select_columns is not None:
            stmt = select(*select_columns)
        else:
            stmt = select(self._model_type)

        if join_params is not None:
            for params in join_params:
                stmt = stmt.join(**params)

        if join_relationships is not None:
            for relationship in join_relationships:
                stmt = stmt.options(
                    joinedload(getattr(self._model_type, relationship))
                )

        if expressions is not None:
            stmt = stmt.where(*expressions)

        if order_by_columns is not None:
            stmt = stmt.order_by(*order_by_columns)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = await db.execute(stmt)

        return result.unique().scalars().all()

    async def aget_by_ids(self, db: AsyncSession, ids: list[int]) -> Sequence[T]:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.id.in_(ids))
        )
        return result.scalars().all()

    async def aget_by_id(
        self,
        db: AsyncSession,
        id_: int,
        join_relationships: list[str] | None = None
    ) -> T | None:
        stmt = (
            select(self._model_type)
            .where(self._model_type.id == id_)
        )

        if join_relationships:
            for relationship in join_relationships:
                stmt = stmt.options(
                    joinedload(getattr(self._model_type, relationship))
                )

        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def aget_by(
        self,
        db: AsyncSession,
        expressions: list[ColumnElement[bool]],
        join_relationships: list[str] | None = None
    ) -> T | None:
        stmt = select(self._model_type)

        if join_relationships:
            for relationship in join_relationships:
                stmt = stmt.options(
                    joinedload(getattr(self._model_type, relationship))
                )

        stmt = stmt.where(*expressions)

        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()


    async def acreate(self, db: AsyncSession, data: dict) -> T:
        instance = self._model_type()

        for name, value in data.items():
            setattr(instance, name, value)

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
