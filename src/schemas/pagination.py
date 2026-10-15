from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1)
