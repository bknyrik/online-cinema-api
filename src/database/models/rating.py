from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    UniqueConstraint,
    Table
)
from sqlalchemy.orm import relationship

from src.database.models.base import Base


class LikeMovieModel(Base):
    __tablename__ = "movie_likes"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE")
    )
    movie = relationship("MovieModel", back_populates="likes")
    profile = relationship("UserProfileModel", back_populates="movie_likes")

    __table_args__ = (
        UniqueConstraint("movie_id", "profile_id"),
    )


class CommentMovieModel(Base):
    __tablename__ = "movie_comments"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE")
    )
    text = Column(Text, nullable=False)
    movie = relationship("MovieModel", back_populates="comments")
    profile = relationship("UserProfileModel", back_populates="movie_comments")


class ReplyCommentModel(Base):
    __tablename__ = "comment_replies"

    id = Column(Integer, primary_key=True)
    comment_id = Column(
        Integer,
        ForeignKey("movie_comments.id", ondelete="CASCADE")
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE")
    )
    text = Column(Text, nullable=False)
    comment = relationship("CommentMovieModel", back_populates="replies")
    profile = relationship("UserProfileModel", back_populates="comment_replies")


class RateModel(Base):
    __tablename__ = "movie_rates"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))
    profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"))
    scale = Column(Integer, nullable=False)
    movie = relationship("MovieModel", back_populates="rates")
    profile = relationship("UserProfileModel", back_populates="rates")

    __table_args__ = (
        UniqueConstraint("movie_id", "profile_id"),
    )


FavoriteMoviesModel = Table(
    "favorite_movies",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("profile_id", ForeignKey("user_profiles.id"), primary_key=True),
)
