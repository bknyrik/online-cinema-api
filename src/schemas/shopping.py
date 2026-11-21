from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from src.schemas.cinema import GenreDetailResponseSchema


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
    cart_id: int
    movie: CartItemMovieDetailSchema
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemCreateRequestSchema(BaseModel):
    movie_id: int


class CartListItemSchema(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime


class CartListResponseSchema(BaseModel):
    carts: list


class CartDetailResponseSchema(BaseModel):
    cart_items: list[CartItemDetailSchema]

    model_config = ConfigDict(from_attributes=True)
