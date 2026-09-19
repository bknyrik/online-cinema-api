from pydantic import BaseModel


class CertificationDetailBaseSchema(BaseModel):
    id: int
    name: str
