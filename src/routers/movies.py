from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import movies as schemas
from src.dependencies.database import get_db
from src.services import movies as services
from src.database.models import movies as models
from src.database.models.accounts import UserModel
from src.dependencies.authentication import get_current_moderator_or_admin
from src.dependencies.movies import (
    MovieFilterDep,
    MovieSearchDep,
    MovieSortDep
)
from src.dependencies.pagination import PaginationDep


router = APIRouter()


@router.get("/movies/", response_model=schemas.MovieListResponseSchema)
async def get_movie_list(
    pagination_data: PaginationDep,
    search_data: MovieSearchDep,
    filter_data: MovieFilterDep,
    sort_data: MovieSortDep,
    db: AsyncSession = Depends(get_db),
    movie_service: services.MovieService = Depends(services.MovieService)
) -> dict:
    return await movie_service.get_movie_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        search_data=search_data,
        sort_data=sort_data
    )


@router.get(
    "/movies/{movie_id}/",
    response_model=schemas.MovieDetailResponseSchema
)
async def get_detail_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: services.MovieService = Depends(services.MovieService)
) -> models.MovieModel:
    return await movie_service.get_detail_movie(
        db=db,
        movie_id=movie_id
    )


@router.post(
    "/movies/",
    response_model=schemas.MovieDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_movie(
    data: schemas.MovieDataRequestSchema,
    movie_service: services.MovieService = Depends(services.MovieService),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> models.MovieModel:
    return await movie_service.create_movie(
        db=db,
        data=data.model_dump()
    )


@router.patch(
    "/movies/{movie_id}/",
    response_model=schemas.MovieDetailResponseSchema
)
async def update_movie(
    movie_id: int,
    data: schemas.MovieUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    movie_service: services.MovieService = Depends(services.MovieService),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> models.MovieModel:
    return await movie_service.update_movie(
        db=db,
        data=data.model_dump(exclude_defaults=True),
        movie_id=movie_id
    )


@router.delete(
    "/movies/{movie_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    movie_service: services.MovieService = Depends(services.MovieService),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> None:
    return await movie_service.delete_movie(
        db=db,
        movie_id=movie_id
    )


@router.get(
    "/genres/",
    response_model=schemas.GenreListResponseSchema
)
async def get_genre_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
) -> dict:
    return await genre_service.get_genre_list(
        db=db,
        pagination_data=pagination_data
    )


@router.get(
    "/genres/{genre_id}/",
    response_model=schemas.GenreMoviesDetailResponseSchema
)
async def get_genre_detail(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
) -> models.GenreModel:
    return await genre_service.get_genre_detail(
        db=db,
        genre_id=genre_id
    )


@router.post(
    "/genres/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.GenreDetailResponseSchema
)
async def create_genre(
    data: schemas.GenreDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> models.GenreModel:
    return await genre_service.create_genre(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/genres/{genre_id}/",
    response_model=schemas.GenreDetailResponseSchema
)
async def update_genre(
    genre_id: int,
    data: schemas.GenreDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> models.GenreModel:
    return await genre_service.update_genre(
        db=db,
        genre_id=genre_id,
        data=data.model_dump()
    )


@router.delete(
    "/genres/{genre_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> None:
    return await genre_service.delete_genre(
        db=db,
        genre_id=genre_id
    )
