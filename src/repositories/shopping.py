from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, func

from src.repositories.base import AsyncBaseRepository
from src.database.models import shopping as models


class CartRepository(AsyncBaseRepository[models.CartModel]):

    def __init__(self) -> None:
        super().__init__(models.CartModel)

    async def aget_all_with_count_cart_items(
        self,
        db: AsyncSession
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
        )
        return result.all()


class CartItemRepository(AsyncBaseRepository[models.CartItemModel]):

    def __init__(self) -> None:
        super().__init__(models.CartItemModel)
