from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import movies as movies_schemas
from src.dependencies.database import get_db
from src.services.movies import MovieService
from src.database.models.movies import MovieModel
from src.database.models.accounts import UserModel
from src.dependencies.services import get_movie_service
from src.dependencies.authentication import get_current_moderator_or_admin
from src.dependencies.movies import (
    MovieFilterDep,
    MovieSearchDep,
    MovieSortDep
)
from src.dependencies.pagination import PaginationDep


router = APIRouter()


@router.get("/", response_model=movies_schemas.MovieListResponseSchema)
async def get_movie_list(
    pagination_data: PaginationDep,
    search_data: MovieSearchDep,
    filter_data: MovieFilterDep,
    sort_data: MovieSortDep,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service)
) -> dict:
    return await movie_service.get_movie_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        search_data=search_data,
        sort_data=sort_data
    )


@router.get(
    "/{movie_id}/",
    response_model=movies_schemas.MovieDetailResponseSchema
)
async def get_detail_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service)
) -> MovieModel:
    return await movie_service.get_detail_movie(
        db=db,
        movie_id=movie_id
    )


@router.post(
    "/",
    response_model=movies_schemas.MovieDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_movie(
    data: movies_schemas.MovieCreateRequestSchema,
    movie_service: MovieService = Depends(get_movie_service),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> MovieModel:
    return await movie_service.create_movie(
        db=db,
        data=data.model_dump()
    )


@router.patch(
    "/{movie_id}/",
    response_model=movies_schemas.MovieDetailResponseSchema
)
async def update_movie(
    movie_id: int,
    data: movies_schemas.MovieUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> MovieModel:
    return await movie_service.update_movie(
        db=db,
        data=data.model_dump(),
        movie_id=movie_id
    )


@router.delete(
    "/{movie_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> None:
    return await movie_service.delete_movie(
        db=db,
        movie_id=movie_id
    )
