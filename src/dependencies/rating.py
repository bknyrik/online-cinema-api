from typing import Annotated

from fastapi import Query, Depends


async def comment_filter_params(
    filter_by_movie_id: int = Query(default=None),
    filter_by_current_user: bool = Query(default=False)
) -> dict:
    return {
        "filter_by_movie_id": filter_by_movie_id,
        "filter_by_by_current_user": filter_by_current_user
    }


CommentFilterDep = Annotated[dict, Depends(comment_filter_params)]
