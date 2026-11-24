from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_serializer, ConfigDict

from src.database.models.order import OrderStatusEnum


class OrderItemMovieDetailSchema(BaseModel):
    name: str
    time: int
    year: int
    genres: list[str]

    @field_serializer("genres")
    def serialize_into_str_names(self, genres: list) -> list[str]:
        return [genre.name for genre in genres]


class OrderItemDetailResponseSchema(BaseModel):
    id: int
    movie: OrderItemMovieDetailSchema
    price_at_order: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponseSchema(BaseModel):
    id: int
    user_id: int
    order_items: list[OrderItemDetailResponseSchema]
    created_at: datetime
    status: OrderStatusEnum

    model_config = ConfigDict(from_attributes=True)
