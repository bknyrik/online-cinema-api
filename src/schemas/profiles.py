import datetime

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, HttpUrl

from src.database.models.accounts import GenderEnum


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


class ProfileDetailResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar: HttpUrl
    gender: GenderEnum
    date_of_birth: datetime.date
    info: str
