from decimal import Decimal

from pydantic import (
    BaseModel,
    UUID4,
    ConfigDict,
    field_validator,
    field_serializer,
    Field
)

from src.schemas.genres import GenreBaseSchema
from src.schemas.certifications import CertificationDetailResponseSchema
from src.schemas.stars import StarDetailResponseSchema


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
    certification: CertificationDetailResponseSchema
    genres: list[GenreBaseSchema]
    stars: list[StarDetailResponseSchema]
    directors: list[DirectorDetailBaseSchema]

    @field_serializer("certification", when_used="json")
    def serialize_into_str_name(
        self,
        item: CertificationDetailResponseSchema
    ) -> str:
        return item.name

    @field_serializer(
        "genres",
        "stars",
        "directors",
        when_used="json"
    )
    def serialize_into_str_names(
        self,
        items: list[
            GenreBaseSchema
            | StarDetailResponseSchema
            | DirectorDetailBaseSchema
            ]
    ) -> list[str]:
        return [item.name for item in items]


class MovieListResponseSchema(BaseModel):
    movies: list[MovieDetailItemSchema]
    total_movies: int
    total_pages: int
    next: str | None = None
    prev: str | None = None


class MovieDetailResponseSchema(MovieDetailBaseSchema):
    certification: CertificationDetailResponseSchema
    genres: list[GenreBaseSchema]
    stars: list[StarDetailResponseSchema]
    directors: list[DirectorDetailBaseSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieDataRequestBaseSchema(BaseModel):
    name: int = Field(min_length=3)
    year: int = Field(ge=1)
    time: int = Field(ge=1)
    imdb: float = Field(ge=1, le=10)
    votes: int = Field(ge=1)
    meta_score: float = Field(ge=1, le=100)
    gross: float = Field(ge=1)
    description: str = Field(min_length=10)
    price: Decimal = Field(ge=1, max_digits=10, decimal_places=2)
    certification: int
    genres: list[int]
    stars: list[int]
    directors: list[int]

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def validate_unique_identifiers(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Identifiers must be unique")

        return value

    model_config = ConfigDict(strict=True)


class MovieCreateRequestSchema(MovieDataRequestBaseSchema):
    ...

class MovieUpdateRequestSchema(MovieDataRequestBaseSchema):
    name: str | None = Field(
        min_length=3,
        default=None,
    )
    year: int | None = Field(
        ge=1,
        default=None,
    )
    time: int | None = Field(
        ge=1,
        default=None,
    )
    imdb: float | None = Field(
        ge=1,
        le=10,
        default=None,
    )
    votes: int | None = Field(
        ge=1,
        default=None,
    )
    meta_score: int | None = Field(
        ge=1,
        le=100,
        default=None,
    )
    gross: float | None = Field(
        ge=1,
        default=None,
    )
    description: str | None = Field(
        min_length=10,
        default=None,
    )
    price: Decimal | None = Field(
        ge=1,
        max_digits=10,
        decimal_places=2,
        default=None,
    )
    certification: int | None = Field(
        default=None,
    )
    genres: list[int] | None = Field(
        default=None,
    )
    stars: list[int] | None = Field(
        default=None,
    )
    directors: list[int] | None = Field(
        default=None,
    )

    model_config = ConfigDict(strict=True)
