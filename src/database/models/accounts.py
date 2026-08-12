from datetime import timezone, datetime, timedelta

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(DateTime(timezone=True), nullable=False)
    group_id = Column(Integer, ForeignKey("user_groups.id"), nullable=False)
    group = relationship(UserGroupModel, back_populates="users")


class AbstractTokenModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    token = Column(
        String(255),
        unique=True,
        nullable=False
    )
    expires_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
        nullable=False
    )
    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
