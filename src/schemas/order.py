from typing import Annotated
from datetime import datetime
from decimal import Decimal

from fastapi import Query
from pydantic import BaseModel, field_serializer, ConfigDict, Field

from src.database.models.order import OrderStatusEnum
from src.schemas.pagination import PaginationParams
from src.schemas.cinema import (
    GenreDetailResponseSchema,
    CertificationDetailResponseSchema
)


class OrderItemMovieDetailSchema(BaseModel):
    name: str
    time: int
    year: int
    price: Decimal
    genres: list[GenreDetailResponseSchema]
    certification: CertificationDetailResponseSchema

    @field_serializer("genres")
    def serialize_into_str_names(
        self,
        genres: list[GenreDetailResponseSchema]
    ) -> list[str]:
        return [genre.name for genre in genres]

    @field_serializer("certification")
    def serialize_into_str_name(
        self,
        certification: CertificationDetailResponseSchema
    ) -> str:
        return certification.name


class OrderItemDetailResponseSchema(BaseModel):
    id: int
    movie: OrderItemMovieDetailSchema
    price_at_order: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponseSchema(BaseModel):
    id: int
    user_id: int
    movies: list[OrderItemMovieDetailSchema]
    created_at: datetime
    status: OrderStatusEnum
    total_amount: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class OrderListItemSchema(OrderDetailResponseSchema):
    movies: int


class OrderListResponseSchema(BaseModel):
    orders: list[OrderListItemSchema]
    total_orders: int
    total_pages: int
    prev: str | None
    next: str | None


class OrderCreateRequestSchema(BaseModel):
    movies: list[int]


class OrderListQueryParams(PaginationParams):
    filter_by_user_id: int | None = Field(default=None)
    filter_by_min_created_at: datetime | None = Field(default=None)
    filter_by_max_created_at: datetime | None = Field(default=None)
    filter_by_status: OrderStatusEnum | None = Field(default=None)


OrderListQuery = Annotated[OrderListQueryParams, Query()]
