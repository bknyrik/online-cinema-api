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


@router.get(
    "/{star_id}/",
    response_model=stars_schemas.StarDetailResponseSchema
)
async def get_star_detail(
    star_id: int,
    db: AsyncSession = Depends(get_db),
    star_service: StarService = Depends(get_star_service)
) -> StarModel:
    return await star_service.get_star_detail(
        db=db,
        star_id=star_id
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=stars_schemas.StarDetailResponseSchema
)
async def create_star(
    data: stars_schemas.StarDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    star_service: StarService = Depends(get_star_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> StarModel:
    return await star_service.create_star(
        db=db,
        data=data.model_dump()
    )
