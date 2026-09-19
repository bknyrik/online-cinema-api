from pydantic import BaseModel


class StarBaseSchema(BaseModel):
    id: int
    name: str


class StarListResponseSchema(BaseModel):
    stars: list[StarBaseSchema]
    total_stars: int
    total_pages: int
    prev: str | None
    next: str | None
