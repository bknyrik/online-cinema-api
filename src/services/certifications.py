from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.database.models.movies import CertificationModel
from src.repositories.movies import CertificationRepository
