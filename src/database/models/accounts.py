from sqlalchemy import Column, Integer, Enum
from enum import StrEnum, auto

from src.database.models.base import Base


class UserGroupEnum(StrEnum):
    USER = auto()
    MODERATOR = auto()
    ADMIN = auto()


class UserGroupModel(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        Enum(UserGroupEnum),
        default=UserGroupEnum.USER,
        nullable=False,
        unique=True
    )
