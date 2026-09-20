from pydantic import BaseModel


class DirectorDetailBaseSchema(BaseModel):
    id: int
    name: str
