from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, func

from src.repositories.base import AsyncBaseRepository
from src.database.models import shopping as models
from src.database.models.order import OrderModel, OrderItemModel


class CartRepository(AsyncBaseRepository[models.CartModel]):

    def __init__(self) -> None:
        super().__init__(models.CartModel)

    async def aget_all_with_count_cart_items(
        self,
        db: AsyncSession,
        limit: int,
        offset: int
    ) -> Sequence[Row]:
        result = await db.execute(
            select(
                self._model_type.id,
                self._model_type.user_id,
                func.count(models.CartItemModel.id).label("cart_items")
            )
            .join(models.CartItemModel, isouter=True)
            .group_by(self._model_type.id)
            .order_by(self._model_type.id)
            .limit(limit)
            .offset(offset)
        )
        return result.all()


class CartItemRepository(AsyncBaseRepository[models.CartItemModel]):

    def __init__(self) -> None:
        super().__init__(models.CartItemModel)


class OrderRepository(AsyncBaseRepository[OrderModel]):

    def __init__(self) -> None:
        super().__init__(OrderModel)

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
                func.count(OrderItemModel.id).label("order_items")
            )
            .join(OrderItemModel)
            .where(*expressions)
            .group_by(self._model_type.id)
            .order_by(self._model_type.id)
            .limit(limit)
            .offset(offset)
        )
        return result.all()


class OrderItemRepository(AsyncBaseRepository[OrderItemModel]):

    def __init__(self) -> None:
        super().__init__(OrderItemModel)
