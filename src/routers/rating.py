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


@router.get("/movie-likes/", response_model=schemas.MovieLikeListResponseSchema)
async def get_movie_like_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await like_service.get_movie_like_list(
        db=db,
        pagination_data=pagination_data,
        current_user=current_user
    )


@router.post(
    "/movie-likes/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MovieLikeDetailResponseSchema
)
async def create_movie_like(
    data: schemas.MovieLikeDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieLikeModel:
    return await like_service.create_movie_like(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/movie-likes/{like_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_movie_like(
    like_id: int,
    db: AsyncSession = Depends(get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await like_service.delete_movie_like(
        db=db,
        like_movie_id=like_id,
        current_user=current_user
    )


@router.get(
    "/movie-comments/",
    response_model=schemas.MovieCommentListResponseSchema
)
async def get_movie_comment_list(
    pagination_data: PaginationDep,
    filter_data: CommentFilterDep,
    db: AsyncSession = Depends(get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(auth.get_current_user),
) -> dict:
    return await comment_service.get_comment_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        current_user=current_user
    )


@router.get(
    "/movie-comments/{comment_id}/",
    response_model=schemas.MovieCommentDetailResponseSchema
)
async def get_movie_comment_detail(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieCommentModel:
    return await comment_service.get_comment_detail(
        db=db,
        comment_id=comment_id
    )


@router.post(
    "/movie-comments/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MovieCommentDetailResponseSchema,
)
async def create_movie_comment(
    data: schemas.MovieCommentCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService)
) -> MovieCommentModel:
    return await comment_service.create_comment(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/movie-comments/{comment_id}/",
    response_model=schemas.MovieCommentDetailResponseSchema
)
async def update_movie_comment(
    comment_id: int,
    data: schemas.MovieCommentUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return await comment_service.update_comment(
        db=db,
        data=data.model_dump(),
        comment_id=comment_id,
        current_user=current_user
    )


@router.delete(
    "/movie-comments/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await comment_service.delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )
