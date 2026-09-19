from pydantic import BaseModel, ConfigDict, Field


class CertificationBaseSchema(BaseModel):
    id: int
    name: str


class CertificationDetailResponseSchema(CertificationBaseSchema):
    ...


class CertificationListResponseSchema(BaseModel):
    certifications: list[CertificationBaseSchema]
    total_certifications: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CertificationDataRequestSchema(BaseModel):
    name: str = Field(min_length=1, strict=True)


class CertificationDataResponseSchema(CertificationBaseSchema):
    ...


class CertificationCreateRequestSchema(CertificationDataRequestSchema):
    ...


class CertificationUpdateRequestSchema(CertificationDataRequestSchema):
    ...
