from typing import Annotated

from decimal import Decimal
from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.database.models.shopping import OrderStatusEnum
from src.schemas.cinema import GenreDetailResponseSchema
from src.schemas.pagination import PaginationParams


class CartItemMovieDetailSchema(BaseModel):
    name: str
    price: Decimal
    genres: list[GenreDetailResponseSchema]
    year: int

    @field_serializer("genres")
    def serialize_into_str_name(
        self,
        genres: list[GenreDetailResponseSchema]
    ) -> list[str]:
        return [genre.name for genre in genres]


class CartItemDetailSchema(BaseModel):
    id: int
    movie: CartItemMovieDetailSchema
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemCreateRequestSchema(BaseModel):
    movie_id: int


class CartListItemSchema(BaseModel):
    id: int
    user_id: int
    cart_items: int


class CartListResponseSchema(BaseModel):
    carts: list[CartListItemSchema]
    total_carts: int
    total_pages: int
    prev: str | None = None
    next: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CartDetailResponseSchema(BaseModel):
    id: int
    user_id: int
    cart_items: list[CartItemDetailSchema]

    model_config = ConfigDict(from_attributes=True)


class CurrentUserCartDetailResponseSchema(CartDetailResponseSchema):
    id: int
    user_id: int = Field(exclude=True)
    cart_items: list[CartItemDetailSchema]


class OrderItemDetailResponseSchema(BaseModel):
    id: int
    movie: CartItemMovieDetailSchema
    price_at_order: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponseSchema(BaseModel):
    id: int
    user_id: int
    order_items: list[OrderItemDetailResponseSchema]
    created_at: datetime
    status: OrderStatusEnum
    total_amount: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class CurrentUserOrderDetailResponseSchema(OrderDetailResponseSchema):
    user_id: int = Field(exclude=True)
    order_items: int


class OrderListItemSchema(OrderDetailResponseSchema):
    order_items: int


class OrderListResponseSchema(BaseModel):
    orders: list[OrderListItemSchema]
    total_orders: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CurrentUserOrderListResponseSchema(OrderListResponseSchema):
    orders: list[CurrentUserOrderDetailResponseSchema]


class OrderListQueryParams(PaginationParams):
    filter_by_user_id: int | None = Field(default=None)
    filter_by_min_created_at: datetime | None = Field(default=None)
    filter_by_max_created_at: datetime | None = Field(default=None)
    filter_by_status: OrderStatusEnum | None = Field(default=None)


OrderListQuery = Annotated[OrderListQueryParams, Query()]
