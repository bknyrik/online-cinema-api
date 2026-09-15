import math

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
