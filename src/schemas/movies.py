from decimal import Decimal

from pydantic import (
    BaseModel,
    UUID4,
    ConfigDict,
    field_validator,
    field_serializer,
    Field
)
from pydantic.types import (
    StrictFloat,
    StrictInt,
    StrictStr
)

from src.schemas.genres import GenreBaseSchema
from src.schemas.certifications import CertificationBaseSchema
from src.schemas.stars import StarBaseSchema


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
    certification: CertificationBaseSchema
    genres: list[GenreBaseSchema]
    stars: list[StarBaseSchema]
    directors: list[DirectorDetailBaseSchema]

    @field_serializer("certification", when_used="json")
    def serialize_into_str_name(
        self,
        item: CertificationBaseSchema
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
            | StarBaseSchema
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
    certification: CertificationBaseSchema
    genres: list[GenreBaseSchema]
    stars: list[StarBaseSchema]
    directors: list[DirectorDetailBaseSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieDataRequestBaseSchema(BaseModel):
    name: StrictStr = Field(min_length=3)
    year: StrictInt = Field(ge=1)
    time: StrictInt = Field(ge=1)
    imdb: StrictFloat = Field(ge=1, le=10)
    votes: StrictInt = Field(ge=1)
    meta_score: StrictFloat = Field(ge=1, le=100)
    gross: StrictFloat = Field(ge=1)
    description: StrictStr = Field(min_length=10)
    price: Decimal = Field(ge=1, max_digits=10, decimal_places=2)
    certification: StrictInt
    genres: list[StrictInt]
    stars: list[StrictInt]
    directors: list[StrictInt]

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def validate_unique_identifiers(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Identifiers must be unique")

        return value


class MovieCreateRequestSchema(MovieDataRequestBaseSchema):
    ...

class MovieUpdateRequestSchema(MovieDataRequestBaseSchema):
    name: StrictStr | None = Field(
        min_length=3,
        default=None,
        exclude_if=lambda value: value is None
    )
    year: StrictInt | None = Field(
        ge=1,
        default=None,
        exclude_if=lambda value: value is None
    )
    time: StrictInt | None = Field(
        ge=1,
        default=None,
        exclude_if=lambda value: value is None
    )
    imdb: StrictFloat | None = Field(
        ge=1,
        le=10,
        default=None,
        exclude_if=lambda value: value is None
    )
    votes: StrictInt| None = Field(
        ge=1,
        default=None,
        exclude_if=lambda value: value is None
    )
    meta_score: StrictFloat | None = Field(
        ge=1,
        le=100,
        default=None,
        exclude_if=lambda value: value is None
    )
    gross: StrictFloat | None = Field(
        ge=1,
        default=None,
        exclude_if=lambda value: value is None
    )
    description: StrictStr | None = Field(
        min_length=10,
        default=None,
        exclude_if=lambda value: value is None
    )
    price: Decimal | None = Field(
        ge=1,
        max_digits=10,
        decimal_places=2,
        default=None,
        exclude_if=lambda value: value is None
    )
    certification: StrictInt | None = Field(
        default=None,
        exclude_if=lambda value: value is None
    )
    genres: list[StrictInt] | None = Field(
        default=None,
        exclude_if=lambda value: value is None
    )
    stars: list[StrictInt] | None = Field(
        default=None,
        exclude_if=lambda value: value is None
    )
    directors: list[StrictInt] | None = Field(
        default=None,
        exclude_if=lambda value: value is None
    )
