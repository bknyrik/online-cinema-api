from pydantic import BaseModel, UUID4, ConfigDict


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


class MovieDetailResponseSchema(MovieDetailBaseSchema):
    certification: CertificationDetailBaseSchema
    genres: list[GenreDetailBaseSchema]
    stars: list[StarDetailBaseSchema]
    directors: list[DirectorDetailBaseSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieCreateRequestSchema(BaseModel):
    name: str
    year: int
    time: int
    imdb: float
    votes: float
    meta_score: int
    gross: float
    description: str
    price: float
    certification: int
    genres: list[int]
    stars: list[int]
    directors: list[int]
