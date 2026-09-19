from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.schemas import stars as stars_schemas
from src.dependencies.services import get_star_service
from src.services.stars import StarService


router = APIRouter()


@router.get(
    "/",
    response_model=stars_schemas.StarListResponseSchema
)
async def get_star_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    star_service: StarService = Depends(get_star_service)
) -> dict:
    return await star_service.get_star_list(
        pagination_data=pagination_data,
        db=db
    )
