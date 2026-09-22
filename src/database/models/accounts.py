from datetime import timezone, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    ForeignKey,
    Boolean,
    UniqueConstraint,
    Text,
    Date
)
from sqlalchemy.orm import relationship
from enum import StrEnum, auto

from src.database.models.base import Base
from src.database.models.rating import FavoriteMoviesModel


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
    users = relationship("UserModel", back_populates="group")


class UserModel(Base):
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
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    group_id = Column(Integer, ForeignKey("user_groups.id"), nullable=False)
    group = relationship(UserGroupModel, back_populates="users")
    activation_token = relationship(
        "ActivationTokenModel",
        back_populates="user",
        single_parent=True
    )
    password_reset_token = relationship(
        "PasswordResetTokenModel",
        back_populates="user",
        single_parent=True
    )
    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="user"
    )
    profile = relationship(
        "UserProfileModel",
        back_populates="user",
        single_parent=True
    )


class AbstractTokenModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    token = Column(
        String(255),
        unique=True,
        nullable=False,
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )
    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    @property
    def has_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class ActivationTokenModel(AbstractTokenModel):
    __tablename__ = "activation_tokens"

    user = relationship(
        UserModel,
        back_populates="activation_token",
        single_parent=True
    )

    __table_args__ = (UniqueConstraint("user_id"),)


class PasswordResetTokenModel(AbstractTokenModel):
    __tablename__ = "password_reset_tokens"

    user = relationship(
        UserModel,
        back_populates="password_reset_token",
        single_parent=True
    )

    __table_args__ = (UniqueConstraint("user_id"),)


class RefreshTokenModel(AbstractTokenModel):
    __tablename__ = "refresh_tokens"

    user = relationship(UserModel, back_populates="refresh_tokens")


class GenderEnum(StrEnum):
    MAN = auto()
    WOMAN = auto()


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    info = Column(Text, nullable=False)
    user = relationship(
        UserModel,
        back_populates="profile",
        single_parent=True
    )
    favorite_movies = relationship(
        "MovieModel",
        secondary="rating.FavoriteMoviesModel"
    )
    movie_likes = relationship(
        "LikeMovieModel",
        back_populates="profile"
    )
    movie_comments = relationship(
        "CommentMovieModel",
        back_populates="profile"
    )
