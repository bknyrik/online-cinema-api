from typing import Annotated
from enum import StrEnum, auto

from fastapi import Depends, Query


class SortingOrderEnum(StrEnum):
    ASC = auto()
    DESC = auto()


async def movie_filter_params(
    filter_by_genres_ids: list[int] = Query(default=None),
    filter_by_min_year: int = Query(default=None),
    filter_by_max_year: int = Query(default=None),
    filter_by_min_time: int = Query(default=None),
    filter_by_max_time: int = Query(default=None),
    filter_by_min_imdb: int = Query(default=None),
    filter_by_max_imdb: int = Query(default=None),
    filter_by_min_price: int = Query(default=None),
    filter_by_max_price: int = Query(default=None)
) -> dict:
    return {
        "genres_ids": filter_by_genres_ids,
        "min_year": filter_by_min_year,
        "max_year": filter_by_max_year,
        "min_time": filter_by_min_time,
        "max_time": filter_by_max_time,
        "min_imdb": filter_by_min_imdb,
        "max_imdb": filter_by_max_imdb,
        "min_price": filter_by_min_price,
        "max_price": filter_by_max_price
    }


async def movie_search_params(
    search_by_name: str = Query(default=None),
    search_by_description: str = Query(default=None),
    search_by_stars_ids: list[int] = Query(default=None),
    search_by_directors_ids: list[int] = Query(default=None)
) -> dict:
    return {
        "name": search_by_name,
        "description": search_by_description,
        "stars": search_by_stars_ids,
        "directors": search_by_directors_ids
    }


async def movie_sort_params(
    sort_by_name: SortingOrderEnum = Query(default=None),
    sort_by_year: SortingOrderEnum = Query(default=None),
    sort_by_time: SortingOrderEnum = Query(default=None),
    sort_by_imdb: SortingOrderEnum = Query(default=None),
    sort_by_votes: SortingOrderEnum = Query(default=None),
    sort_by_meta_score: SortingOrderEnum = Query(default=None),
    sort_by_gross: SortingOrderEnum = Query(default=None),
    sort_by_price: SortingOrderEnum = Query(default=None)
) -> dict[str, SortingOrderEnum | None]:
    return {
        "sort_by_name": sort_by_name,
        "sort_by_year": sort_by_year,
        "sort_by_time": sort_by_time,
        "sort_by_imdb": sort_by_imdb,
        "sort_by_votes": sort_by_votes,
        "sort_by_meta_score": sort_by_meta_score,
        "sort_by_gross": sort_by_gross,
        "sort_by_price": sort_by_price
    }


MovieFilterDep = Annotated[dict, Depends(movie_filter_params)]
MovieSearchDep = Annotated[dict, Depends(movie_search_params)]
MovieSortDep = Annotated[
    dict[str, SortingOrderEnum | None],
    Depends(movie_sort_params)
]
