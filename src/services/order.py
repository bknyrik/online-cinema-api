from decimal import Decimal

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from src.repositories import order as repositories
from src.repositories.cinema import MovieRepository

from src.database.models import order as models
from src.database.models.accounts import UserModel
from src.database.models.cinema import MovieModel
from src.services import mixins



