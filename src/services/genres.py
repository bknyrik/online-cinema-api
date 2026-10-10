from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.movies import GenreRepository
from src.services.mixins import (
    PaginationLimitOffsetMixin,
    ModelItemsMixin
)
from src.database.models.movies import GenreModel



