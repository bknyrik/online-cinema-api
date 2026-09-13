from pydantic import BaseModel


class GenreDetailBaseSchema(BaseModel):
    id: int
    name: str


class GenreDetailItemSchema(GenreDetailBaseSchema):
    movies: int


class GenreListResponseSchema(BaseModel):
    genres: list[GenreDetailItemSchema]
    total_genres: int
    total_pages: int
    prev: str | None
    next: str | None
