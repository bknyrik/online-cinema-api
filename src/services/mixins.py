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
        query_params = {
            key: value for key, value in query_params.items()
            if value is not None
        }

        query_params["page"] = page - 1 if page > 1 else page
        prev_page = (
            f"{url}?{parse.urlencode(query_params)}" if page > 1 else None
        )

        query_params["page"] = page + 1
        next_page = (
            f"{url}?{parse.urlencode(query_params)}"
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


class ModelItemsMixin[T]:

    @staticmethod
    def validate_item_by_id_not_found(
        item: T | None,
        id_: int,
        item_type: str
    ) -> None:
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{item_type} with id {id_} not found"
            )
