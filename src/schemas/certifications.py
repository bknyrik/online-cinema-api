from pydantic import BaseModel, ConfigDict, Field


class CertificationDetailBaseSchema(BaseModel):
    id: int
    name: str


class CertificationDetailResponseSchema(CertificationDetailBaseSchema):
    ...


class CertificationListResponseSchema(BaseModel):
    certifications: list[CertificationDetailBaseSchema]
    total_certifications: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CertificationCreateUpdateRequestSchema(BaseModel):
    name: str = Field(min_length=1, strict=True)
