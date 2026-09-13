from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.genres import GenreService
from src.dependencies.services import get_genre_service
from src.dependencies.pagination import PaginationDep
from src.schemas.genres import GenreListResponseSchema


router = APIRouter()


@router.get("/", response_model=GenreListResponseSchema)
async def get_genre_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service)
) -> dict:
    return await genre_service.get_genre_list(db)
