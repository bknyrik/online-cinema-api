from sqlalchemy import Column, String, Integer

from src.database.models.base import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)
