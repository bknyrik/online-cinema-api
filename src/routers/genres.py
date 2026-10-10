from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.authentication import get_current_moderator_or_admin
from src.services.genres import GenreService
from src.dependencies.services import get_genre_service
from src.dependencies.pagination import PaginationDep
from src.schemas import genres as genres_schemas
from src.database.models.movies import GenreModel
from src.database.models.accounts import UserModel


router = APIRouter()


