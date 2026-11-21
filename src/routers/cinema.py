from fastapi import APIRouter, status

from src.schemas import cinema as schemas
from src.schemas import pagination
from src.dependencies import database, authentication, services
from src.database.models import cinema as models


router = APIRouter()


@router.get("/movies/", response_model=schemas.MovieListResponseSchema)
async def get_movie_list(
    query_params: schemas.MovieListQuery,
    db: database.AsyncSessionDep,
    movie_service: services.MovieServiceDep
) -> dict:
    return await movie_service.get_movie_list(
        db=db,
        query_params=query_params.model_dump()
    )


@router.get(
    "/movies/{movie_id}/",
    response_model=schemas.MovieDetailResponseSchema
)
async def get_detail_movie(
    movie_id: int,
    db: database.AsyncSessionDep,
    movie_service: services.MovieServiceDep
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
    db: database.AsyncSessionDep,
    movie_service: services.MovieServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    movie_service: services.MovieServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    movie_service: services.MovieServiceDep,
    current_user: authentication.CurrentAdminDep
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
    query_params: pagination.PaginationQuery,
    db: database.AsyncSessionDep,
    genre_service: services.GenreServiceDep,
) -> dict:
    return await genre_service.get_genre_list(
        db=db,
        query_params=query_params.model_dump()
    )


@router.get(
    "/genres/{genre_id}/",
    response_model=schemas.GenreMoviesDetailResponseSchema
)
async def get_genre_detail(
    genre_id: int,
    db: database.AsyncSessionDep,
    genre_service: services.GenreServiceDep,
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
    db: database.AsyncSessionDep,
    genre_service: services.GenreServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    genre_service: services.GenreServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    genre_service: services.GenreServiceDep,
    current_user: authentication.CurrentAdminDep
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
    query_params: pagination.PaginationQuery,
    db: database.AsyncSessionDep,
    certification_service: services.CertificationServiceDep,
) -> dict:
    return await certification_service.get_certification_list(
        query_params=query_params.model_dump(),
        db=db
    )


@router.get(
    "/certifications/{certification_id}/",
    response_model=schemas.CertificationDetailResponseSchema
)
async def get_certification_detail(
    certification_id: int,
    db: database.AsyncSessionDep,
    certification_service: services.CertificationServiceDep,
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
    db: database.AsyncSessionDep,
    certification_service: services.CertificationServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    certification_service: services.CertificationServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    certification_service: services.CertificationServiceDep,
    current_user: authentication.CurrentAdminDep
) -> None:
    return await certification_service.delete_certification(
        db=db,
        certification_id=certification_id
    )


@router.get("/directors/", response_model=schemas.DirectorListResponseSchema)
async def get_director_list(
    query_params: pagination.PaginationQuery,
    db: database.AsyncSessionDep,
    director_service: services.DirectorServiceDep
) -> dict:
    return await director_service.get_director_list(
        db=db,
        query_params=query_params.model_dump()
    )


@router.get(
    "/directors/{director_id}/",
    response_model=schemas.DirectorDetailResponseSchema
)
async def get_director_detail(
    director_id: int,
    db: database.AsyncSessionDep,
    director_service: services.DirectorServiceDep
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
    db: database.AsyncSessionDep,
    director_service: services.DirectorServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    director_service: services.DirectorServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    director_service: services.DirectorServiceDep,
    current_user: authentication.CurrentAdminDep
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
    query_params: pagination.PaginationQuery,
    db: database.AsyncSessionDep,
    star_service: services.StarServiceDep,
) -> dict:
    return await star_service.get_star_list(
        query_params=query_params.model_dump(),
        db=db
    )


@router.get(
    "/stars/{star_id}/",
    response_model=schemas.StarDetailResponseSchema
)
async def get_star_detail(
    star_id: int,
    db: database.AsyncSessionDep,
    star_service: services.StarServiceDep,
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
    db: database.AsyncSessionDep,
    star_service: services.StarServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    star_service: services.StarServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
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
    db: database.AsyncSessionDep,
    star_service: services.StarServiceDep,
    current_user: authentication.CurrentModeratorOrAdminDep
) -> None:
    return await star_service.delete_star(
        db=db,
        star_id=star_id
    )
