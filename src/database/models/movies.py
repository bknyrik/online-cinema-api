import uuid

from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
    Uuid,
    Float,
    Text,
    DECIMAL,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.database.models.base import Base
from src.database.models.rating import FavoriteMoviesModel

MoviesGenresModel = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True)
)

MoviesStarsModel = Table(
    "movie_stars",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("star_id", ForeignKey("stars.id"), primary_key=True)
)

MoviesDirectorsModel = Table(
    "movie_directors",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("director_id", ForeignKey("directors.id"), primary_key=True)
)


class GenreModel(Base):
    __tablename__ = "genres"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)
    movies = relationship(
        "MovieModel",
        secondary=MoviesGenresModel,
        back_populates="genres"
    )

    def __eq__(self, other: "GenreModel") -> bool:
        return self.name == other.name


class StarModel(Base):
    __tablename__ = "stars"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)
    movies = relationship(
        "MovieModel",
        secondary=MoviesStarsModel,
        back_populates="stars"
    )

    def __eq__(self, other: "StarModel") -> bool:
        return self.name == other.name


class DirectorModel(Base):
    __tablename__ = "directors"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    movies = relationship(
        "MovieModel",
        secondary=MoviesDirectorsModel,
        back_populates="directors"
    )

    def __eq__(self, other: "DirectorModel") -> bool:
        return self.name == other.name


class CertificationModel(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    movies = relationship("MovieModel", back_populates="certification")

    def __eq__(self, other: "CertificationModel") -> bool:
        return self.name == other.name


class MovieModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(
        Uuid,
        nullable=False,
        unique=True,
        default=uuid.uuid4
    )
    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    imdb = Column(Float, nullable=False)
    votes = Column(Integer, nullable=False)
    meta_score = Column(Float, nullable=True)
    gross = Column(Float, nullable=True)
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    certification_id = Column(
        Integer,
        ForeignKey("certifications.id", ondelete="CASCADE"),
        nullable=False,
    )
    certification = relationship(CertificationModel, back_populates="movies")
    genres = relationship(
        GenreModel,
        secondary=MoviesGenresModel,
        back_populates="movies"
    )
    stars = relationship(
        StarModel,
        secondary=MoviesStarsModel,
        back_populates="movies"
    )
    directors = relationship(
        DirectorModel,
        secondary=MoviesDirectorsModel,
        back_populates="movies"
    )
    likes = relationship(
        "rating.LikeMovieModel",
        back_populates="movie",
    )
    comments = relationship(
        "rating.CommentMovieModel",
        back_populates="movie"
    )
    rates = relationship(
        "rating.RateModel",
        back_populates="movie"
    )
    profiles = relationship(
        "UserProfileModel",
        secondary=FavoriteMoviesModel,
        back_populates="favorite_movies"
    )

    __table_args__ = (
        UniqueConstraint("name", "year", "time", name="name_year_time_unique"),
    )

    def __eq__(self, other: "MovieModel") -> bool:
        return (
            self.name == other.name
            and self.year == other.year
            and self.time == other.time
        )
