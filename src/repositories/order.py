from typing import Sequence

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import AsyncBaseRepository
from src.database.models import order as models


class OrderRepository(AsyncBaseRepository[models.OrderModel]):

    def __init__(self) -> None:
        super().__init__(models.OrderModel)

    async def aget_all_with_order_items_count(
        self,
        db: AsyncSession,
        expressions: list,
        limit: int,
        offset: int
    ) -> Sequence[Row]:
        result = await db.execute(
            select(
                self._model_type.id,
                self._model_type.created_at,
                self._model_type.user_id,
                self._model_type.status,
                self._model_type.total_amount,
                func.count(models.OrderItemModel.id).label("order_items")
            )
            .join(models.OrderItemModel)
            .where(*expressions)
            .group_by(self._model_type.id)
            .order_by(self._model_type.id)
            .limit(limit)
            .offset(offset)
        )
        return result.all()


class OrderItemRepository(AsyncBaseRepository[models.OrderItemModel]):

    def __init__(self) -> None:
        super().__init__(models.OrderItemModel)
