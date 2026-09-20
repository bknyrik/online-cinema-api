from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.services.directors import DirectorService
from src.schemas import directors as schemas
from src.dependencies.services import get_director_service
from src.dependencies.pagination import PaginationDep
from src.database.models.movies import DirectorModel
from src.dependencies.authentication import get_current_moderator_or_admin
from src.database.models.accounts import UserModel


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


@router.post(
    "/",
    response_model=schemas.DirectorDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_director(
    data: schemas.DirectorDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    director_service: DirectorService = Depends(get_director_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> DirectorModel:
    return await director_service.create_director(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema
)
async def update_director(
    director_id: int,
    data: schemas.DirectorDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    director_service: DirectorService = Depends(get_director_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> DirectorModel:
    return await director_service.update_director(
        db=db,
        data=data.model_dump(),
        director_id=director_id
    )


@router.delete(
    "/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema,
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_director(
    director_id: int,
    db: AsyncSession = Depends(get_db),
    director_service: DirectorService = Depends(get_director_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> None:
    return await director_service.delete_director(
        db=db,
        director_id=director_id
    )
