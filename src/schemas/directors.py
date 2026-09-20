from pydantic import BaseModel


class DirectorDetailResponseSchema(BaseModel):
    id: int
    name: str
