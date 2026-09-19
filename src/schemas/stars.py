from pydantic import BaseModel


class StarDetailBaseSchema(BaseModel):
    id: int
    name: str
