from pydantic import BaseModel


class DirectorDetailResponseSchema(BaseModel):
    id: int
    name: str


class DirectorListResponseSchema(BaseModel):
    directors: list[DirectorDetailResponseSchema]
    total_directors: int
    total_pages: int
    prev: str | None
    next: str | None
