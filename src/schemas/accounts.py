from pydantic import BaseModel, EmailStr, field_validator

from src.database.models.accounts import UserGroupEnum
from src.database.validators import accounts


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str
    group: UserGroupEnum = UserGroupEnum.USER

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return accounts.validate_email(value)


class UserRegistrationResponseSchema(BaseModel):
    id: int
    email: EmailStr


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str
