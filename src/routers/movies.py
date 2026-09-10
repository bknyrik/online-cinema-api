from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.movies import (
    MovieDetailResponseSchema,
    MovieCreateRequestSchema
)
from src.dependencies.database import get_db
from src.services.movies import MovieService
from src.database.models.movies import MovieModel
from src.database.models.accounts import UserModel
from src.dependencies.services import get_movie_service
from src.dependencies.authentication import get_current_moderator_user


router = APIRouter()


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_detail_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service)
) -> MovieModel:
    return await movie_service.get_detail_movie(
        db=db,
        movie_id=movie_id
    )


@router.post("/", response_model=MovieDetailResponseSchema)
async def create_movie(
    data: MovieCreateRequestSchema,
    movie_service: MovieService = Depends(get_movie_service),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_moderator_user)
) -> MovieModel:
    return await movie_service.create_movie(
        db=db,
        data=data.model_dump()
    )


@router.delete("/{movie_id/}")
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: UserModel = Depends(get_current_moderator_user)
) -> None:
    return await movie_service.delete_movie(
        db=db,
        movie_id=movie_id
    )
