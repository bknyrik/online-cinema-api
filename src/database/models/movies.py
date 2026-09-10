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


MovieGenresModel = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True)
)

MovieStarsModel = Table(
    "movie_stars",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("stars.id"), primary_key=True)
)

MovieDirectorsModel = Table(
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
        secondary=MovieGenresModel,
        back_populates="genres"
    )


class StarModel(Base):
    __tablename__ = "stars"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)
    movies = relationship(
        "MovieModel",
        secondary=MovieStarsModel,
        back_populates="stars"
    )


class DirectorModel(Base):
    __tablename__ = "directors"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    movies = relationship(
        "MovieModel",
        secondary=MovieDirectorsModel,
        back_populates="directors"
    )


class CertificationModel(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    movies = relationship("MovieModel", back_populates="certification")


class MovieModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Uuid, nullable=True, unique=True)
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
        secondary=MovieGenresModel,
        back_populates="movies"
    )
    stars = relationship(
        StarModel,
        secondary=MovieStarsModel,
        back_populates="movies"
    )
    directors = relationship(
        DirectorModel,
        secondary=MovieDirectorsModel,
        back_populates="movies"
    )

    __table_args__ = (
        UniqueConstraint("name", "year", "time", name="name_year_time_unique"),
    )
