from src.repositories.base import AsyncBaseRepository
from src.database.models import order as models


class OrderRepository(AsyncBaseRepository[models.OrderModel]):

    def __init__(self) -> None:
        super().__init__(models.OrderModel)


class OrderItemRepository(AsyncBaseRepository[models.OrderItemModel]):

    def __init__(self) -> None:
        super().__init__(models.OrderItemModel)
