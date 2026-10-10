from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.authentication import get_current_moderator_or_admin
from src.dependencies.pagination import PaginationDep
from src.dependencies.services import get_certification_service
from src.services.certifications import CertificationService
from src.schemas import certifications
from src.database.models.movies import CertificationModel
from src.database.models.accounts import UserModel


router = APIRouter()


