from urllib import parse
from enum import StrEnum, auto

from fastapi import HTTPException, status
from sqlalchemy import UnaryExpression, ColumnElement
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
        not_found_ids = []
        for id_ in ids:
            if all(item.id != id_ for item in items):
                not_found_ids.append(id_)

        if not_found_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"{item_type} with ids "
                    + ", ".join(str(id_) for id_ in not_found_ids)
                    + " not found"
                )
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
                column = getattr(cls.MODEL_TYPE, name)
                sort_columns.append(
                    column if order == SortingOrderEnum.ASC else column.desc()
                )

        return sort_columns


class SearchItemsMixin:

    @classmethod
    def get_search_expressions(
        cls,
        search_data: dict
    ) -> list[ColumnElement[bool]]:
        search_data = {
            key.replace("search_by_", ""): value
            for key, value in search_data.items()
        }

        search_expressions = []

        for name, value in search_data.items():
            if value is not None:
                if isinstance(value, str):
                    search_expressions.append(
                        getattr(cls.MODEL_TYPE, name).icontains(value)
                    )

                if name.endswith("_ids"):
                    column = getattr(cls.MODEL_TYPE, name.replace("_ids", ""))
                    child_model = column.prop.argument
                    search_expressions.append(
                        column.any(child_model.id.in_(value))
                    )

        return search_expressions


class FilterItemsMixin:

    @classmethod
    def _get_min_max_filter_expressions(
        cls,
        filter_data: dict
    ) -> list[ColumnElement[bool]]:
        min_max_keys = tuple(
            (min_key, max_key) for min_key, max_key in zip(
                (key for key in filter_data.keys() if key.startswith("min_")),
                (key for key in filter_data.keys() if key.startswith("max_"))
            )
        )

        expressions = []

        for min_key, max_key in min_max_keys:
            column = getattr(cls.MODEL_TYPE, min_key.replace("min_", ""))
            min_value, max_value = filter_data[min_key], filter_data[max_key]

            if min_value is not None and max_value is not None:
                expressions.append(column.between(min_value, max_value))

            elif min_value is not None:
                expressions.append(column >= min_value)

            elif max_value is not None:
                expressions.append(column <= max_value)

        return expressions

    @classmethod
    def _get_single_id_expressions(
        cls,
        filter_data: dict
    ) -> list[ColumnElement[bool]]:
        return [
            getattr(cls.MODEL_TYPE, name) == filter_data[name]
            for name, value in filter_data.items()
            if name.endswith("_id") and value is not None
        ]

    @classmethod
    def _get_multiple_ids_expressions(
        cls,
        filter_data: dict
    ) -> list[ColumnElement[bool]]:
        expressions = []

        for name, value in filter_data.items():
            if name.endswith("_ids") and value is not None:
                column = getattr(cls.MODEL_TYPE, name.replace("_ids", ""))
                child_model = column.prop.argument

                expressions.append(column.any(child_model.id.in_(value)))

        return expressions

    @classmethod
    def get_filter_expressions(cls, filter_data: dict) -> list[ColumnElement[bool]]:
        filter_data = {
            key.replace("filter_by_", ""): value
            for key, value in filter_data.items()
        }

        return (
            cls._get_min_max_filter_expressions(filter_data) +
            cls._get_single_id_expressions(filter_data) +
            cls._get_multiple_ids_expressions(filter_data)
        )
