from pydantic import BaseModel, field_serializer


class OrderItemMovieDetailSchema(BaseModel):
    name: str
    description: str
    year: int
    genres: list[str]

    @field_serializer("genres")
    def serialize_into_str_names(self, genres: list) -> list[str]:
        return [genre.name for genre in genres]
