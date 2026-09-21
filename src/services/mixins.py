from urllib import parse
from enum import StrEnum, auto

from fastapi import HTTPException, status
from sqlalchemy import UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute


class SortingOrderEnum(StrEnum):
    ASC = auto()
    DESC = auto()


class PaginationLimitOffsetMixin:

    @staticmethod
    def get_limit_offset(pagination_data: dict[str, int]) -> tuple[int, int]:
        return (
            pagination_data["per_page"],
            (pagination_data["page"] - 1) * pagination_data["per_page"]
        )

    @staticmethod
    def get_total_pages(total_items: int, per_page: int) -> int:
        return (total_items + per_page - 1) // per_page

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

    @staticmethod
    def validate_item_by_attrs_exists(
        item: T | None,
        attrs: dict,
        item_type: str
    ) -> None:
        if item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{item_type} with " +
                    ", ".join(
                        f"{key} '{value}'" for key, value in attrs.items()
                    ) + " exists"
                )
            )

    @staticmethod
    def validate_item_by_attrs_with_another_item_exists(
        item: T | None,
        another_item: T | None,
        attrs: dict,
        item_type: str
    ) -> None:
        if another_item and another_item != item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{item_type} with " +
                    ", ".join(
                        f"{key} '{value}'" for key, value in attrs.items()
                    ) + " exists"
                )
            )

    @staticmethod
    def validate_items_by_ids_not_found(
        items: list,
        ids: list[int],
        item_type: str
    ) -> None:
        for id_ in ids:
            if not all(item.id != id_ for item in items):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{item_type} with id {id_} not found"
                )


class SortingItemsMixin:

    @classmethod
    def get_sort_columns(
        cls,
        sort_data: dict
    ) -> list[InstrumentedAttribute | UnaryExpression]:
        sort_data = {
            key.replace("sort_by_", ""): value
            for key, value in sort_data.items()
        }
        sort_columns = []

        for name, order in sort_data.items():
            if order is not None:
                column = getattr(cls._model_type, name)
                sort_columns.append(
                    column if order == SortingOrderEnum.ASC else column.desc()
                )

        return sort_columns
