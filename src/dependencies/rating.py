from typing import Annotated

from fastapi import Query, Depends, HTTPException, status

from src.database.models.accounts import UserModel
from src.dependencies.authentication import get_current_user


async def comment_filter_params(
    filter_by_movie_id: int = Query(default=None),
    filter_by_profile_id: int = Query(default=None),
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    if current_user.profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if (
        filter_by_profile_id is not None
        and current_user.group.name not in ("admin", "moderator")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin or moderator to perform this action"
        )

    return {
        "filter_by_movie_id": filter_by_movie_id,
        "filter_by_profile_id": filter_by_profile_id
    }


CommentFilterDep = Annotated[dict, Depends(comment_filter_params)]
