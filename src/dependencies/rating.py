from typing import Annotated

from fastapi import Query, Depends, HTTPException, status

from src.database.models.accounts import UserModel
from src.dependencies.authentication import get_current_user


async def rating_filter_params(
    filter_by_profile_id: int = Query(default=None),
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    if (
        filter_by_profile_id is not None
        and current_user.group.name not in ("admin", "moderator")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin or moderator to perform this action"
        )

    return {
        "filter_by_profile_id": filter_by_profile_id
    }


async def comment_filter_params(
    filter_by_movie_id: int = Query(default=None),
    rating_filter_queries: dict = Depends(rating_filter_params)
) -> dict:
    return {
        "filter_by_movie_id": filter_by_movie_id,
        **rating_filter_queries
    }


async def comment_reply_filter_params(
    filter_by_comment_id: int = Query(default=None),
    rating_filter_queries: dict = Depends(rating_filter_params)
) -> dict:
    return {
        "filter_by_comment_id": filter_by_comment_id,
        **rating_filter_queries
    }


CommentFilterDep = Annotated[dict, Depends(comment_filter_params)]
CommentReplyFilterDep = Annotated[dict, Depends(comment_reply_filter_params)]
