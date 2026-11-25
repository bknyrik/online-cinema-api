from enum import StrEnum, auto

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.database.models.base import Base
from src.database.models.cinema import MovieModel
