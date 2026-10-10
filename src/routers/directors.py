from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.directors import DirectorService
from src.schemas import directors as schemas
from src.dependencies.services import get_director_service
from src.dependencies.pagination import PaginationDep
from src.database.models.movies import DirectorModel
from src.dependencies.authentication import get_current_moderator_or_admin
from src.database.models.accounts import UserModel


router = APIRouter()


