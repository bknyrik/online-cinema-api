from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

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
    user_id: int
    cart_items: int


class CartListResponseSchema(BaseModel):
    carts: list[CartListItemSchema]
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
