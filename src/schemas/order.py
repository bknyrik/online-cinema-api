from typing import Annotated
from datetime import datetime
from decimal import Decimal

from fastapi import Query
from pydantic import BaseModel, field_serializer, ConfigDict, Field

from src.database.models.order import OrderStatusEnum
from src.schemas.pagination import PaginationParams
from src.schemas.cinema import GenreDetailResponseSchema



