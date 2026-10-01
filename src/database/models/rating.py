from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime,
    UniqueConstraint,
    Table
)
from sqlalchemy.orm import relationship

from src.database.models.base import Base


class MovieLikeModel(Base):
    __tablename__ = "movie_likes"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    movie = relationship("MovieModel", back_populates="likes")
    profile = relationship("UserProfileModel", back_populates="movie_likes")

    __table_args__ = (
        UniqueConstraint(
            "movie_id",
            "profile_id",
            name="movie_likes_movie_id_profile_id_unique"
        ),
    )


class MovieCommentModel(Base):
    __tablename__ = "movie_comments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    text = Column(Text, nullable=False)
    movie = relationship("MovieModel", back_populates="comments")
    profile = relationship("UserProfileModel", back_populates="movie_comments")
    replies = relationship("CommentReplyModel", back_populates="comment")
    likes = relationship("CommentLikeModel", back_populates="comment")


class CommentReplyModel(Base):
    __tablename__ = "comment_replies"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    comment_id = Column(
        Integer,
        ForeignKey("movie_comments.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    text = Column(Text, nullable=False)
    comment = relationship("MovieCommentModel", back_populates="replies")
    profile = relationship("UserProfileModel", back_populates="comment_replies")


class CommentLikeModel(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    comment_id = Column(
        Integer,
        ForeignKey("movie_comments.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    comment = relationship(MovieCommentModel, back_populates="likes")
    profile = relationship("UserProfileModel", back_populates="comment_likes")

    __table_args__ = (
        UniqueConstraint(
            "comment_id",
            "profile_id",
            name="comment_likes_comment_id_profile_id_unique"
        ),
    )


class MovieRateModel(Base):
    __tablename__ = "movie_rates"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    scale = Column(Integer, nullable=False)
    movie = relationship("MovieModel", back_populates="rates")
    profile = relationship("UserProfileModel", back_populates="rates")

    __table_args__ = (
        UniqueConstraint(
            "movie_id",
            "profile_id",
            name="movie_rates_movie_id_profile_id_unique"
        ),
    )


class FavoriteMoviesModel(Base):
    __tablename__ = "favorite_movies"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    movie = relationship("MovieModel")
    profile = relationship("UserProfileModel", back_populates="favorite_movies")

    __table_args__ = (
        UniqueConstraint(
            "movie_id",
            "profile_id",
            name="favorite_movies_movie_id_profile_id_unique"
        ),
    )
