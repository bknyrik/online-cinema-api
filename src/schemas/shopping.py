from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartItemDetailSchema(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime


class CartItemCreateRequestSchema(BaseModel):
    movie_id: int


class CartListResponseSchema(BaseModel):
    cart_items: list[CartItemDetailSchema]

    model_config = ConfigDict(from_attributes=True)
