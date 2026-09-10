from pydantic import BaseModel, UUID4


class MovieDetailBaseSchema(BaseModel):
    id: int
    uuid: UUID4
    name: str
    year: int
    time: int
    imdb: float
    votes: float
    meta_score: int
    gross: float
    description: str
    price: float


class MovieDetailItemSchema(MovieDetailBaseSchema):
    certification: str
    genres: list[str]
    stars: list[str]
    directors: list[str]
