from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.directors import DirectorService
from src.schemas import directors as schemas
from src.dependencies.services import get_director_service
from src.dependencies.pagination import PaginationDep
from src.database.models.movies import DirectorModel


router = APIRouter()


@router.get("/", response_model=schemas.DirectorListResponseSchema)
async def get_director_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    director_service: DirectorService = Depends(get_director_service)
) -> dict:
    return await director_service.get_director_list(
        db=db,
        pagination_data=pagination_data
    )


@router.get(
    "/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema
)
async def get_director_detail(
    director_id: int,
    db: AsyncSession = Depends(get_db),
    director_service: DirectorService = Depends(get_director_service)
) -> DirectorModel:
    return await director_service.get_director_detail(
        db=db,
        director_id=director_id
    )
