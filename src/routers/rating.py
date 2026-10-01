from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.dependencies import authentication as auth
from src.dependencies.rating import CommentFilterDep
from src.services import rating as services
from src.schemas import rating as schemas
from src.database.models.accounts import UserModel
from src.database.models.rating import MovieLikeModel, MovieCommentModel


router = APIRouter()


@router.get("/likes-movies/", response_model=schemas.LikeMovieListResponseSchema)
async def get_like_movie_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await like_movie_service.get_movie_like_list(
        db=db,
        pagination_data=pagination_data,
        current_user=current_user
    )


@router.post(
    "/likes-movies/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LikeMovieDetailResponseSchema
)
async def create_like_movie(
    data: schemas.LikeMovieDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieLikeModel:
    return await like_movie_service.create_like_movie(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/likes-movies/{like_movie_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_like_movie(
    like_movie_id: int,
    db: AsyncSession = Depends(get_db),
    like_movie_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await like_movie_service.delete_like_movie(
        db=db,
        like_movie_id=like_movie_id,
        current_user=current_user
    )


@router.get(
    "/comments/",
    response_model=schemas.CommentMovieListResponseSchema
)
async def get_comment_list(
    pagination_data: PaginationDep,
    filter_data: CommentFilterDep,
    db: AsyncSession = Depends(get_db),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService),
    current_user: UserModel = Depends(auth.get_current_user),
) -> dict:
    return await comment_service.get_comment_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        current_user=current_user
    )


@router.get(
    "/comments/{comment_id}/",
    response_model=schemas.CommentMovieDetailResponseSchema
)
async def get_comment_detail(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieCommentModel:
    return await comment_service.get_comment_detail(
        db=db,
        comment_id=comment_id
    )


@router.post(
    "/comments/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CommentMovieDetailResponseSchema,
)
async def create_comment(
    data: schemas.CommentMovieDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService)
) -> MovieCommentModel:
    return await comment_service.create_comment(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/comment/{comment_id}/",
    response_model=schemas.CommentMovieDetailResponseSchema
)
async def update_comment(
    comment_id: int,
    data: schemas.CommentMovieUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return await comment_service.update_comment(
        db=db,
        data=data.model_dump(),
        comment_id=comment_id,
        current_user=current_user
    )


@router.delete(
    "/comments/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    comment_service: services.CommentMovieService = Depends(services.CommentMovieService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await comment_service.delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )
