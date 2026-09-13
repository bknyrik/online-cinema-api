from pydantic import BaseModel, ConfigDict, field_serializer


class GenreDetailBaseSchema(BaseModel):
    id: int
    name: str


class GenreListItemSchema(GenreDetailBaseSchema):
    movies: list

    @field_serializer("movies", when_used="json")
    def serialize_movies_into_count(self, movies: list) -> int:
        return len(movies)


class GenreListResponseSchema(BaseModel):
    genres: list[GenreListItemSchema]
    total_genres: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)
