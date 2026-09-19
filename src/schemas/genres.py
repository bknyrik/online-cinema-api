from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import StrictStr


class GenreBaseSchema(BaseModel):
    id: int
    name: str


class GenreListItemSchema(GenreBaseSchema):
    movies: int


class GenreListResponseSchema(BaseModel):
    genres: list[GenreListItemSchema]
    total_genres: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class GenreDetailMoviesSchema(BaseModel):
    id: int
    name: str
    year: int
    time: int
    imdb: float
    description: str


class GenreDetailResponseSchema(GenreBaseSchema):
    movies: list[GenreDetailMoviesSchema]

    model_config = ConfigDict(from_attributes=True)


class GenreCreateUpdateRequestSchema(BaseModel):
    name: StrictStr = Field(min_length=5)
