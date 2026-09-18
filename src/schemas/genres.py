from pydantic import BaseModel, ConfigDict


class GenreDetailBaseSchema(BaseModel):
    id: int
    name: str


class GenreListItemSchema(GenreDetailBaseSchema):
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
    imdb: int
    description: str


class GenreDetailResponseSchema(GenreDetailBaseSchema):
    movies: list[GenreDetailMoviesSchema]

    model_config = ConfigDict(from_attributes=True)
