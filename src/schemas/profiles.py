import datetime

from pydantic import BaseModel, HttpUrl

from src.database.models.accounts import GenderEnum


class ProfileDetailResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar: HttpUrl
    gender: GenderEnum
    date_of_birth: datetime.date
    info: str
