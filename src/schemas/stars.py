from pydantic import BaseModel


class StarBaseSchema(BaseModel):
    id: int
    name: str
