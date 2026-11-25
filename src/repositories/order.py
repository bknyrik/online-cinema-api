from typing import Sequence

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import AsyncBaseRepository
from src.database.models import order as models



