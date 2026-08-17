from fastapi import HTTPException, status
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
        try:
            return accounts.validate_email(value)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str) -> str:
        try:
            return accounts.validate_password(value)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )


class UserRegistrationResponseSchema(BaseModel):
    id: int
    email: EmailStr


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserDetailResponseSchema(BaseModel):
    id: int
    email: EmailStr
    group: UserGroupEnum


class ChangeUserGroupRequestSchema(BaseModel):
    group: UserGroupEnum


class MessageResponseSchema(BaseModel):
    message: str
