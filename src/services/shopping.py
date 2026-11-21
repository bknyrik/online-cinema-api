from src.database.models import shopping as models
from src.repositories import shopping as repositories


class CartService:

    def __init__(self) -> None:
        self.model_type = models.CartModel
        self.cart_repository = repositories.CartRepository()
        self.cart_item_repository = repositories.CartItemRepository()
