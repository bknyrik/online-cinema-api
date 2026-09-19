from pydantic import BaseModel, ConfigDict


class CertificationDetailBaseSchema(BaseModel):
    id: int
    name: str


class CertificationListResponseSchema(BaseModel):
    certifications: list[CertificationDetailBaseSchema]
    total_certifications: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)
