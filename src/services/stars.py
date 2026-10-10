from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import StarModel
from src.repositories.movies import StarRepository
from src.services import mixins



