from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import (
    database,
    authentication,
    rating,
)
from src.services import rating as services
from src.schemas import rating as rating_schemas
from src.schemas import cinema as cinema_schemas
from src.schemas import pagination
from src.database.models.accounts import UserModel
from src.database.models import rating as models


router = APIRouter()


@router.get("/movie-likes/", response_model=rating_schemas.MovieLikeListResponseSchema)
async def get_movie_like_list(
    query_params: rating_schemas.MovieLikeListQuery,
    db: AsyncSession = Depends(database.get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> dict:
    return await like_service.get_movie_like_list(
        db=db,
        query_params=query_params.model_dump(),
        current_user=current_user
    )


@router.post(
    "/movie-likes/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.MovieLikeDetailResponseSchema
)
async def create_movie_like(
    data: rating_schemas.MovieLikeDataRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.MovieLikeModel:
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
    db: AsyncSession = Depends(database.get_db),
    like_service: services.MovieLikeService = Depends(services.MovieLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await like_service.delete_movie_like(
        db=db,
        like_movie_id=like_id,
        current_user=current_user
    )


@router.get(
    "/movie-comments/",
    response_model=rating_schemas.MovieCommentListResponseSchema
)
async def get_movie_comment_list(
    query_params: rating_schemas.MovieCommentListQuery,
    db: AsyncSession = Depends(database.get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(authentication.get_current_user),
) -> dict:
    return await comment_service.get_movie_comment_list(
        db=db,
        query_params=query_params.model_dump(),
        current_user=current_user
    )


@router.get(
    "/movie-comments/{comment_id}/",
    response_model=rating_schemas.MovieCommentDetailResponseSchema
)
async def get_movie_comment_detail(
    comment_id: int,
    db: AsyncSession = Depends(database.get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.MovieCommentModel:
    return await comment_service.get_movie_comment_detail(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )


@router.post(
    "/movie-comments/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.MovieCommentDetailResponseSchema,
)
async def create_movie_comment(
    data: rating_schemas.MovieCommentCreateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    current_user: UserModel = Depends(authentication.get_current_user),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService)
) -> models.MovieCommentModel:
    return await comment_service.create_movie_comment(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/movie-comments/{comment_id}/",
    response_model=rating_schemas.MovieCommentDetailResponseSchema
)
async def update_movie_comment(
    comment_id: int,
    data: rating_schemas.MovieCommentUpdateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(authentication.get_current_user),
) -> models.MovieCommentModel:
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
    db: AsyncSession = Depends(database.get_db),
    comment_service: services.MovieCommentService = Depends(services.MovieCommentService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await comment_service.delete_movie_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user
    )


@router.get(
    "/comment-replies/",
    response_model=rating_schemas.CommentReplyListResponseSchema
)
async def get_comment_reply_list(
    query_params: rating_schemas.CommentReplyListQuery,
    db: AsyncSession = Depends(database.get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> dict:
    return await reply_service.get_comment_reply_list(
        db=db,
        query_params=query_params.model_dump(),
        current_user=current_user
    )


@router.get(
    "/comment-replies/{reply_id}/",
    response_model=rating_schemas.CommentReplyDetailResponseSchema
)
async def get_comment_reply_detail(
    reply_id: int,
    db: AsyncSession = Depends(database.get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.CommentReplyModel:
    return await reply_service.get_comment_reply_detail(
        reply_id=reply_id,
        db=db,
        current_user=current_user
    )


@router.post(
    "/comment-replies/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.CommentReplyDetailResponseSchema
)
async def create_comment_reply(
    data: rating_schemas.CommentReplyCreateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.CommentReplyModel:
    return await reply_service.create_comment_reply(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/comment-replies/{reply_id}/",
    response_model=rating_schemas.CommentReplyDetailResponseSchema
)
async def update_comment_reply(
    reply_id: int,
    data: rating_schemas.CommentReplyUpdateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.CommentReplyModel:
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
    db: AsyncSession = Depends(database.get_db),
    reply_service: services.CommentReplyService = Depends(services.CommentReplyService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await reply_service.delete_comment_reply(
        db=db,
        reply_id=reply_id,
        current_user=current_user,
    )


@router.get(
    "/comment-likes/",
    response_model=rating_schemas.CommentLikeListResponseSchema
)
async def get_comment_like_list(
    filter_data: rating.CommentReplyFilterDep,
    pagination_data: pagination.PaginationQuery,
    db: AsyncSession = Depends(database.get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> dict:
    return await like_service.get_comment_like_list(
        db=db,
        pagination_data=pagination_data.model_dump(),
        filter_data=filter_data,
        current_user=current_user
    )


@router.post(
    "/comment-likes/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.CommentLikeDetailResponseSchema
)
async def create_comment_like(
    data: rating_schemas.CommentLikeCreateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.CommentLikeModel:
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
    db: AsyncSession = Depends(database.get_db),
    like_service: services.CommentLikeService = Depends(services.CommentLikeService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await like_service.delete_comment_like(
        db=db,
        like_id=like_id,
        current_user=current_user
    )


@router.get(
    "/movie-rates/",
    response_model=rating_schemas.MovieRateListResponseSchema,
)
async def get_movie_rate_list(
    filter_data: rating.CommentFilterDep,
    pagination_data: pagination.PaginationQuery,
    db: AsyncSession = Depends(database.get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> dict:
    return await rate_service.get_movie_rate_list(
        pagination_data=pagination_data.model_dump(),
        filter_data=filter_data,
        db=db,
        current_user=current_user
    )


@router.get(
    "/movie-rates/{rate_id}/",
    response_model=rating_schemas.MovieRateDetailResponseSchema,
)
async def get_movie_rate_detail(
    rate_id: int,
    db: AsyncSession = Depends(database.get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.MovieRateModel:
    return await rate_service.get_movie_rate_detail(
        db=db,
        rate_id=rate_id,
        current_user=current_user
    )


@router.post(
    "/movie-rates/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.MovieRateDetailResponseSchema
)
async def create_movie_rate(
    data: rating_schemas.MovieRateCreateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.MovieRateModel:
    return await rate_service.create_movie_rate(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.put(
    "/movie-rates/{rate_id}/",
    response_model=rating_schemas.MovieRateDetailResponseSchema
)
async def update_movie_rate(
    rate_id: int,
    data: rating_schemas.MovieRateUpdateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.MovieRateModel:
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
    db: AsyncSession = Depends(database.get_db),
    rate_service: services.MovieRateService = Depends(services.MovieRateService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await rate_service.delete_movie_rate(
        db=db,
        rate_id=rate_id,
        current_user=current_user
    )


@router.get(
    "/movie-favorites/",
    response_model=cinema_schemas.MovieListResponseSchema
)
async def get_favorite_movie_list(
    pagination_data: pagination.PaginationQuery,
    search_data: cinema_schemas.MovieSearchSchema = Depends(cinema_schemas.MovieSearchSchema),
    filter_data: cinema_schemas.MovieFilterSchema = Depends(cinema_schemas.MovieFilterSchema),
    sort_data: cinema_schemas.MovieListResponseSchema = Depends(cinema_schemas.MovieSortingSchema),
    db: AsyncSession = Depends(database.get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> dict:
    return await favorite_service.get_favorite_movie_list(
        db=db,
        filter_data=filter_data.model_dump(),
        pagination_data=pagination_data.model_dump(),
        search_data=search_data.model_dump(),
        sort_data=sort_data.model_dump(),
        current_user=current_user
    )


@router.post(
    "/movie-favorites/",
    status_code=status.HTTP_201_CREATED,
    response_model=rating_schemas.FavoriteMovieDetailResponseSchema
)
async def add_movie_to_favorites(
    data: rating_schemas.FavoriteMovieCreateRequestSchema,
    db: AsyncSession = Depends(database.get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> models.FavoriteMovieModel:
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
    db: AsyncSession = Depends(database.get_db),
    favorite_service: services.FavoriteMovieService = Depends(services.FavoriteMovieService),
    current_user: UserModel = Depends(authentication.get_current_user),
) -> None:
    return await favorite_service.delete_movie_from_favorites(
        db=db,
        favorite_id=favorite_id,
        current_user=current_user
    )
