from datetime import datetime

from pydantic import BaseModel


class CartItemDetailSchema(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime
