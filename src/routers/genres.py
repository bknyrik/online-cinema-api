from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.authentication import get_current_moderator_or_admin
from src.services.genres import GenreService
from src.dependencies.services import get_genre_service
from src.dependencies.pagination import PaginationDep
from src.schemas.genres import (
    GenreListResponseSchema,
    GenreDetailResponseSchema,
    GenreCreateUpdateRequestSchema,
    GenreDetailBaseSchema
)
from src.database.models.movies import GenreModel
from src.database.models.accounts import UserModel


router = APIRouter()


@router.get("/", response_model=GenreListResponseSchema)
async def get_genre_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service)
) -> dict:
    return await genre_service.get_genre_list(
        db=db,
        pagination_data=pagination_data
    )


@router.get("/{genre_id}/", response_model=GenreDetailResponseSchema)
async def get_genre_detail(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service)
) -> GenreModel:
    return await genre_service.get_genre_detail(
        db=db,
        genre_id=genre_id
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GenreDetailBaseSchema
)
async def create_genre(
    data: GenreCreateUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> GenreModel:
    return await genre_service.create_genre(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/{genre_id}/",
    response_model=GenreDetailBaseSchema
)
async def update_genre(
    genre_id: int,
    data: GenreCreateUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service)
) -> GenreModel:
    return await genre_service.update_genre(
        db=db,
        genre_id=genre_id,
        data=data.model_dump()
    )


@router.delete("/{genre_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    genre_service: GenreService = Depends(get_genre_service)
) -> None:
    return await genre_service.delete_genre(
        db=db,
        genre_id=genre_id
    )
