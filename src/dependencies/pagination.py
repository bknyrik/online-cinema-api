from typing import Annotated

from fastapi import Query, Depends


async def pagination_params(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=10)
) -> dict[str, int]:
    return {"page": page, "per_page": per_page}


PaginationDep = Annotated[dict, Depends(pagination_params)]
