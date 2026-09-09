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


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)


class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    movies = relationship("Movie", back_populates="certification")


class Movie(Base):
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
    certification = relationship(Certification, back_populates="movies")

    __table_args__ = (
        UniqueConstraint("name", "year", "time", name="name_year_time_unique"),
    )


MovieGenresModel = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True)
)
