from src.repositories.base import AsyncBaseRepository
from src.database.models import shopping as models


class CartRepository(AsyncBaseRepository[models.CartModel]):

    def __init__(self) -> None:
        super().__init__(models.CartModel)


class CartItemRepository(AsyncBaseRepository[models.CartItemModel]):

    def __init__(self) -> None:
        super().__init__(models.CartItemModel)
