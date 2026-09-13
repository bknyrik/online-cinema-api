from decimal import Decimal

from pydantic import (
    BaseModel,
    UUID4,
    ConfigDict,
    field_validator,
    Field
)
from pydantic.types import (
    StrictFloat,
    StrictInt
)


class CertificationDetailBaseSchema(BaseModel):
    id: int
    name: str


class GenreDetailBaseSchema(BaseModel):
    id: int
    name: str


class StarDetailBaseSchema(BaseModel):
    id: int
    name: str


class DirectorDetailBaseSchema(BaseModel):
    id: int
    name: str


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


class MovieListResponseSchema(BaseModel):
    movies: list[MovieDetailItemSchema]
    total_movies: int
    total_pages: int
    next: str | None = None
    prev: str | None = None


class MovieDetailResponseSchema(MovieDetailBaseSchema):
    certification: CertificationDetailBaseSchema
    genres: list[GenreDetailBaseSchema]
    stars: list[StarDetailBaseSchema]
    directors: list[DirectorDetailBaseSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieDataRequestBaseSchema(BaseModel):
    name: str = Field(min_length=3)
    year: StrictInt = Field(ge=1)
    time: StrictInt = Field(ge=1)
    imdb: StrictFloat = Field(ge=1, max_digits=1, le=10)
    votes: StrictInt = Field(ge=1)
    meta_score: StrictFloat = Field(ge=1, le=100)
    gross: StrictFloat = Field(ge=1)
    description: str = Field(min_length=10)
    price: Decimal = Field(ge=1)
    certification: int
    genres: list[int]
    stars: list[int]
    directors: list[int]

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def validate_unique_ids(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Ids must be unique")

        return value


class MovieCreateRequestSchema(MovieDataRequestBaseSchema):
    ...

class MovieUpdateRequestSchema(BaseModel):
    name: str | None = None
    year: int | None = None
    time: int | None = None
    imdb: float | None = None
    votes: int | None = None
    meta_score: float | None = None
    gross: float | None = None
    description: str | None = None
    price: Decimal | None = None
    certification: int | None = None
    genres: list[int] | None = None
    stars: list[int] | None = None
    directors: list[int] | None = None
