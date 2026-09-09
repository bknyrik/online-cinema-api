from sqlalchemy import Column, String, Integer

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
