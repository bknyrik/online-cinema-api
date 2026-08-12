from pydantic import BaseModel, EmailStr

from src.database.models.accounts import UserGroupEnum


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str
    group: UserGroupEnum = UserGroupEnum.USER


class UserRegistrationResponseSchema(BaseModel):
    id: int
    email: EmailStr
    group: UserGroupEnum
