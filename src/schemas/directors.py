from pydantic import BaseModel, Field


class DirectorDetailResponseSchema(BaseModel):
    id: int
    name: str


class DirectorListResponseSchema(BaseModel):
    directors: list[DirectorDetailResponseSchema]
    total_directors: int
    total_pages: int
    prev: str | None
    next: str | None


class DirectorDataRequestSchema(BaseModel):
    name: str = Field(min_length=5, strict=True)
