from pydantic import BaseModel


class GenreDetailBaseSchema(BaseModel):
    id: int
    name: str


class GenreDetailItemSchema(GenreDetailBaseSchema):
    movies: int
