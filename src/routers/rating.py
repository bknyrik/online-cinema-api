from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.dependencies import authentication as auth
from src.dependencies.rating import CommentFilterDep, CommentReplyFilterDep
from src.dependencies.cinema import MovieFilterDep, MovieSearchDep, MovieSortDep
from src.services import rating as services
from src.schemas import rating as schemas
from src.schemas.cinema import MovieListResponseSchema
from src.database.models.accounts import UserModel
from src.database.models.rating import (
    MovieLikeModel,
    MovieCommentModel,
    CommentReplyModel,
    CommentLikeModel,
    MovieRateModel,
    FavoriteMovieModel
)


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
    return await comment_service.get_movie_comment_list(
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
    return await comment_service.get_movie_comment_detail(
        db=db,
        comment_id=comment_id,
        current_user=current_user
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
    return await comment_service.create_movie_comment(
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
    return await comment_service.update_movie_comment(
        db=db,
        data=data.model_dump(),
        comment_id=comment_id,
        current_user=current_user
    )


@router.delete(
    "/movie-comments/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_movie_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await comment_service.delete_movie_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )


@router.get(
    "/comment-replies/",
    response_model=schemas.CommentReplyListResponseSchema
)
async def get_comment_reply_list(
    filter_data: CommentReplyFilterDep,
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await reply_service.get_comment_reply_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        current_user=current_user
    )


@router.get(
    "/comment-replies/{reply_id}/",
    response_model=schemas.CommentReplyDetailResponseSchema
)
async def get_comment_reply_detail(
    reply_id: int,
    db: AsyncSession = Depends(get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> CommentReplyModel:
    return await reply_service.get_comment_reply_detail(
        reply_id=reply_id,
        db=db,
        current_user=current_user
    )


@router.post(
    "/comment-replies/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CommentReplyDetailResponseSchema
)
async def create_comment_reply(
    data: schemas.CommentReplyCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(auth.get_current_user)
):
    return await reply_service.create_comment_reply(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/comment-replies/{reply_id}/",
    response_model=schemas.CommentReplyDetailResponseSchema
)
async def update_comment_reply(
    reply_id: int,
    data: schemas.CommentReplyUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> CommentReplyModel:
    return await reply_service.update_comment_reply(
        db=db,
        reply_id=reply_id,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/comment-replies/{reply_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment_reply(
    reply_id: int,
    db: AsyncSession = Depends(get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await reply_service.delete_comment_reply(
        db=db,
        reply_id=reply_id,
        current_user=current_user,
    )


@router.get(
    "/comment-likes/",
    response_model=schemas.CommentLikeListResponseSchema
)
async def get_comment_like_list(
    pagination_data: PaginationDep,
    filter_data: CommentReplyFilterDep,
    db: AsyncSession = Depends(get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await like_service.get_comment_like_list(
        db=db,
        pagination_data=pagination_data,
        filter_data=filter_data,
        current_user=current_user
    )


@router.post(
    "/comment-likes/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CommentLikeDetailResponseSchema
)
async def create_comment_like(
    data: schemas.CommentLikeCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> CommentLikeModel:
    return await like_service.create_comment_like(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/comment-likes/{like_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment_like(
    like_id: int,
    db: AsyncSession = Depends(get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await like_service.delete_comment_like(
        db=db,
        like_id=like_id,
        current_user=current_user
    )


@router.get(
    "/movie-rates/",
    response_model=schemas.MovieRateDetailResponseSchema,
)
async def get_movie_rate_list(
    pagination_data: PaginationDep,
    filter_data: CommentFilterDep,
    db: AsyncSession = Depends(get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await rate_service.get_movie_rate_list(
        pagination_data=pagination_data,
        filter_data=filter_data,
        db=db,
        current_user=current_user
    )


@router.get(
    "/movie-rates/{rate_id}/",
    response_model=schemas.MovieRateDetailResponseSchema,
)
async def get_movie_rate_detail(
    rate_id: int,
    db: AsyncSession = Depends(get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieRateModel:
    return await rate_service.get_movie_rate_detail(
        db=db,
        rate_id=rate_id,
        current_user=current_user
    )


@router.post(
    "/movie-rates/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MovieRateDetailResponseSchema
)
async def create_movie_rate(
    data: schemas.MovieRateCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieRateModel:
    return await rate_service.create_movie_rate(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/movies-rates/{rate_id}/",
    response_model=schemas.MovieRateDetailResponseSchema
)
async def update_movie_rate(
    rate_id: int,
    data: schemas.MovieRateUpdateRequestSchema,
    db: AsyncSession = Depends(get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> MovieRateModel:
    return await rate_service.update_movie_rate(
        db=db,
        rate_id=rate_id,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/movie-rates/{rate_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_movie_rate(
    rate_id: int,
    db: AsyncSession = Depends(get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> None:
    return await rate_service.delete_movie_rate(
        db=db,
        rate_id=rate_id,
        current_user=current_user
    )


@router.get(
    "/movie-favorites/",
    response_model=MovieListResponseSchema
)
async def get_favorite_movie_list(
    pagination_data: PaginationDep,
    search_data: MovieSearchDep,
    filter_data: MovieFilterDep,
    sort_data: MovieSortDep,
    db: AsyncSession = Depends(get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> dict:
    return await favorite_service.get_favorite_movie_list(
        db=db,
        filter_data=filter_data,
        pagination_data=pagination_data,
        search_data=search_data,
        sort_data=sort_data,
        current_user=current_user
    )


@router.post(
    "/movie-favorites/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FavoriteMovieDetailResponseSchema
)
async def add_movie_to_favorites(
    data: schemas.FavoriteMovieCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(auth.get_current_user)
) -> FavoriteMovieModel:
    return await favorite_service.add_movie_to_favorites(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/movie-favorites/{favorite_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_movie_from_favorites(
    favorite_id: int,
    db: AsyncSession = Depends(get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(auth.get_current_user),
) -> None:
    return await favorite_service.delete_movie_from_favorites(
        db=db,
        favorite_id=favorite_id,
        current_user=current_user
    )
