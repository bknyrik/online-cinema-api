from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import movies as schemas
from src.dependencies import database, authentication, cinema, pagination
from src.services import movies as services
from src.database.models import cinema as models
from src.database.models.accounts import UserModel


router = APIRouter()


@router.get("/movies/", response_model=schemas.MovieListResponseSchema)
async def get_movie_list(
    pagination_data: pagination.PaginationDep,
    search_data: cinema.MovieSearchDep,
    filter_data: cinema.MovieFilterDep,
    sort_data: cinema.MovieSortDep,
    db: AsyncSession = Depends(database.get_db),
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
    db: AsyncSession = Depends(database.get_db),
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
    db: AsyncSession = Depends(database.get_db),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
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
    db: AsyncSession = Depends(database.get_db),
    movie_service: services.MovieService = Depends(services.MovieService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
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
    db: AsyncSession = Depends(database.get_db),
    movie_service: services.MovieService = Depends(services.MovieService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
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
    pagination_data: pagination.PaginationDep,
    db: AsyncSession = Depends(database.get_db),
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
    db: AsyncSession = Depends(database.get_db),
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
    db: AsyncSession = Depends(database.get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
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
    db: AsyncSession = Depends(database.get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
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
    db: AsyncSession = Depends(database.get_db),
    genre_service: services.GenreService = Depends(services.GenreService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> None:
    return await genre_service.delete_genre(
        db=db,
        genre_id=genre_id
    )


@router.get(
    "/certifications/",
    response_model=schemas.CertificationListResponseSchema
)
async def get_certification_list(
    pagination_data: pagination.PaginationDep,
    db: AsyncSession = Depends(database.get_db),
    certification_service: services.CertificationService = Depends(services.CertificationService),
) -> dict:
    return await certification_service.get_certification_list(
        pagination_data=pagination_data,
        db=db
    )


@router.get(
    "/certifications/{certification_id}/",
    response_model=schemas.CertificationDetailResponseSchema
)
async def get_certification_detail(
    certification_id: int,
    db: AsyncSession = Depends(database.get_db),
    certification_service: services.CertificationService = Depends(services.CertificationService),
) -> models.CertificationModel:
    return await certification_service.get_certification_detail(
        db=db,
        certification_id=certification_id
    )


@router.post(
    "/certifications/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CertificationDetailResponseSchema
)
async def create_certification(
    data: schemas.CertificationDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    certification_service: services.CertificationService = Depends(services.CertificationService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.CertificationModel:
    return await certification_service.create_certification(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/certifications/{certification_id}/",
    response_model=schemas.CertificationDetailResponseSchema
)
async def update_certification(
    certification_id: int,
    data: schemas.CertificationDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    certification_service: services.CertificationService = Depends(services.CertificationService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.CertificationModel:
    return await certification_service.update_certification(
        db=db,
        certification_id=certification_id,
        data=data.model_dump()
    )


@router.delete(
    "/certifications/{certification_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_certification(
    certification_id: int,
    db: AsyncSession = Depends(database.get_db),
    certification_service: services.CertificationService = Depends(services.CertificationService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> None:
    return await certification_service.delete_certification(
        db=db,
        certification_id=certification_id
    )


@router.get("/directors/", response_model=schemas.DirectorListResponseSchema)
async def get_director_list(
    pagination_data: pagination.PaginationDep,
    db: AsyncSession = Depends(database.get_db),
    director_service: services.DirectorService = Depends(services.DirectorService)
) -> dict:
    return await director_service.get_director_list(
        db=db,
        pagination_data=pagination_data
    )


@router.get(
    "/directors/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema
)
async def get_director_detail(
    director_id: int,
    db: AsyncSession = Depends(database.get_db),
    director_service: services.DirectorService = Depends(services.DirectorService)
) -> models.DirectorModel:
    return await director_service.get_director_detail(
        db=db,
        director_id=director_id
    )


@router.post(
    "/directors/",
    response_model=schemas.DirectorDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_director(
    data: schemas.DirectorDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    director_service: services.DirectorService = Depends(services.DirectorService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.DirectorModel:
    return await director_service.create_director(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/directors/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema
)
async def update_director(
    director_id: int,
    data: schemas.DirectorDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    director_service: services.DirectorService = Depends(services.DirectorService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.DirectorModel:
    return await director_service.update_director(
        db=db,
        data=data.model_dump(),
        director_id=director_id
    )


@router.delete(
    "/directors/{director_id}/",
     status_code=status.HTTP_204_NO_CONTENT
)
async def delete_director(
    director_id: int,
    db: AsyncSession = Depends(database.get_db),
    director_service: services.DirectorService = Depends(services.DirectorService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> None:
    return await director_service.delete_director(
        db=db,
        director_id=director_id
    )


@router.get(
    "/stars/",
    response_model=schemas.StarListResponseSchema
)
async def get_star_list(
    pagination_data: pagination.PaginationDep,
    db: AsyncSession = Depends(database.get_db),
    star_service: services.StarService = Depends(services.StarService),
) -> dict:
    return await star_service.get_star_list(
        pagination_data=pagination_data,
        db=db
    )


@router.get(
    "/stars/{star_id}/",
    response_model=schemas.StarDetailResponseSchema
)
async def get_star_detail(
    star_id: int,
    db: AsyncSession = Depends(database.get_db),
    star_service: services.StarService = Depends(services.StarService),
) -> models.StarModel:
    return await star_service.get_star_detail(
        db=db,
        star_id=star_id
    )


@router.post(
    "/stars/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.StarDetailResponseSchema
)
async def create_star(
    data: schemas.StarDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    star_service: services.StarService = Depends(services.StarService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.StarModel:
    return await star_service.create_star(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/stars/{star_id}/",
    response_model=schemas.StarDetailResponseSchema
)
async def update_star(
    star_id: int,
    data: schemas.StarDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    star_service: services.StarService = Depends(services.StarService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> models.StarModel:
    return await star_service.update_star(
        db=db,
        data=data.model_dump(),
        star_id=star_id
    )


@router.delete(
    "/stars/{star_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_star(
    star_id: int,
    db: AsyncSession = Depends(database.get_db),
    star_service: services.StarService = Depends(services.StarService),
    current_user: UserModel = Depends(authentication.get_current_moderator_or_admin)
) -> None:
    return await star_service.delete_star(
        db=db,
        star_id=star_id
    )
