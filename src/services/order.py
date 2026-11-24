from src.repositories import order as repositories
from src.repositories.cinema import MovieRepository

from src.database.models import order as models


class OrderService:

    def __init__(self) -> None:
        self.model_type = models.OrderModel
        self.order_repository = repositories.OrderRepository()
        self.order_item_repository = repositories.OrderItemRepository()
        self.movie_repository = MovieRepository()
