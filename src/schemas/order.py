from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_serializer, ConfigDict

from src.database.models.order import OrderStatusEnum
from src.schemas.cinema import (
    GenreDetailResponseSchema,
    CertificationDetailResponseSchema
)


class OrderItemMovieDetailSchema(BaseModel):
    name: str
    time: int
    year: int
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
    total_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreateRequestSchema(BaseModel):
    movies: list[int]
