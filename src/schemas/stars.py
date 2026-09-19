from pydantic import BaseModel, ConfigDict, Field


class StarBaseSchema(BaseModel):
    id: int
    name: str


class StarListResponseSchema(BaseModel):
    stars: list[StarBaseSchema]
    total_stars: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class StarDataRequestSchema(BaseModel):
    name: str = Field(min_length=3, strict=True)
