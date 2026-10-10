from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.schemas import stars as stars_schemas
from src.dependencies.services import get_star_service
from src.dependencies.authentication import get_current_moderator_or_admin
from src.services.stars import StarService
from src.database.models.movies import StarModel
from src.database.models.accounts import UserModel


router = APIRouter()


