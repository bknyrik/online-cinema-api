from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
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
        UniqueConstraint(
            "movie_id",
            "profile_id",
            name="movie_id_profile_id_unique"
        )
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
