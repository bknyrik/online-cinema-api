import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status, Form, UploadFile, File
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator

from src.database.models.accounts import UserGroupEnum, GenderEnum
from src.database.validators import accounts


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str

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


class ActivateUserAccountRequestSchema(BaseModel):
    activation_token: str
    email: EmailStr


class ReactivateUserAccountRequestSchema(BaseModel):
    email: EmailStr


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class LogoutRequestSchema(BaseModel):
    refresh_token: str


class UserDetailResponseSchema(BaseModel):
    id: int
    email: EmailStr
    group: UserGroupEnum


class ChangeUserGroupRequestSchema(BaseModel):
    group: UserGroupEnum


class ChangeUserPasswordRequestSchema(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password", mode="before")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        try:
            return accounts.validate_password(value)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )


class ResetUserPasswordRequestSchema(BaseModel):
    email: EmailStr

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


class ResetPasswordCompleteRequestSchema(BaseModel):
    token: str
    email: EmailStr
    password: str

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


class RefreshAccessTokenRequestSchema(BaseModel):
    refresh_token: str
    email: EmailStr


class RefreshAccessTokenResponseSchema(BaseModel):
    access_token: str


class MessageResponseSchema(BaseModel):
    message: str


class ProfileFormSchema(BaseModel):
    first_name: str = Form()
    last_name: str = Form()
    avatar: UploadFile = File(...)
    gender: GenderEnum = Form()
    date_of_birth: datetime.date = Form()
    info: str = Form()

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(),
        last_name: str = Form(),
        avatar: UploadFile = File(...),
        gender: GenderEnum = Form(),
        date_of_birth: datetime.date = Form(),
        info: str = Form()
    ) -> "ProfileFormSchema":
        return cls(
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            gender=gender,
            date_of_birth=date_of_birth,
            info=info
        )


class UserProfileFormData(BaseModel):
    first_name: str | None = Form()
    last_name: str | None = Form()
    avatar: UploadFile | None = File(...)
    gender: GenderEnum | None = Form()
    date_of_birth: datetime.date | None = Form()
    info: str | None = Form()

    @classmethod
    def as_form(
        cls,
        first_name: str | None = Form(default=None),
        last_name: str | None = Form(default=None),
        avatar: UploadFile | None = File(default=None),
        gender: GenderEnum | None = Form(default=None),
        date_of_birth: datetime.date | None = Form(default=None),
        info: str | None = Form(default=None)
    ) -> "UserProfileFormData":
        return cls(
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,
            gender=gender,
            date_of_birth=date_of_birth,
            info=info
        )


class UserProfileDetailResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar: HttpUrl
    gender: GenderEnum
    date_of_birth: datetime.date
    info: str


UserProfileForm = Annotated[
    UserProfileFormData,
    Depends(UserProfileFormData.as_form)
]
