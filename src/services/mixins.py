import math
from urllib import parse

from fastapi import HTTPException, status


class PaginationLimitOffsetMixin:

    @staticmethod
    def get_limit_offset(pagination_data: dict[str, int]) -> tuple[int, int]:
        return (
            pagination_data["per_page"],
            (pagination_data["page"] - 1) * pagination_data["per_page"]
        )

    @staticmethod
    def get_total_pages(total_items: int, per_page: int) -> int:
        return math.ceil(total_items / per_page)

    @staticmethod
    def get_prev_next_urls_pages(
        url: str,
        page: int,
        total_pages: int,
        query_params: dict
    ) -> tuple[str | None, str | None]:
        prev_page = url + parse.urlencode(query_params) if page > 1 else None
        next_page = (
            url + parse.urlencode(query_params)
            if page < total_pages else None
        )
        return prev_page, next_page

    @staticmethod
    def validate_page_not_found(
        page: int,
        total_pages: int,
        total_items: int
    ) -> None:
        if page > total_pages and total_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
