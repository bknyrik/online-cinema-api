from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.dependencies.profiles import get_current_user_profile
from src.services import rating as services
from src.schemas import rating as schemas
from src.database.models.accounts import UserProfileModel
from src.database.models.rating import LikeMovieModel, CommentMovieModel


router = APIRouter()


@router.get("/likes-movies/", response_model=schemas.LikeMovieListResponseSchema)
async def get_like_movie_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.LikeMovieService = Depends(services.LikeMovieService),
    current_user_profile: UserProfileModel = Depends(get_current_user_profile)
) -> dict:
    return await like_movie_service.get_like_movie_list(
        db=db,
        pagination_data=pagination_data,
        current_user_profile=current_user_profile
    )


@router.post(
    "/likes-movies/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LikeMovieDetailResponseSchema
)
async def create_like_movie(
    data: schemas.LikeMovieDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.LikeMovieService = Depends(services.LikeMovieService),
    current_user_profile: UserProfileModel = Depends(get_current_user_profile)
) -> LikeMovieModel:
    return await like_movie_service.create_like_movie(
        db=db,
        data=data.model_dump(),
        current_user_profile=current_user_profile
    )


@router.delete(
    "/likes-movies/{like_movie_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_like_movie(
    like_movie_id: int,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.LikeMovieService = Depends(services.LikeMovieService),
    current_user_profile: UserProfileModel = Depends(get_current_user_profile)
) -> None:
    return await like_movie_service.delete_like_movie(
        db=db,
        like_movie_id=like_movie_id,
        current_user_profile=current_user_profile
    )


@router.post(
    "/comments/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LikeMovieDetailResponseSchema,
)
async def create_comment(
    data: schemas.CommentMovieDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user_profile: UserProfileModel = Depends(get_current_user_profile),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService)
) -> CommentMovieModel:
    return await comment_service.create_comment(
        db=db,
        data=data.model_dump(),
        current_user_profile=current_user_profile
    )
