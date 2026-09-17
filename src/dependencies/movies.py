from typing import Annotated
from enum import StrEnum, auto

from fastapi import Depends, Query


class SortingOrderEnum(StrEnum):
    ASC = auto()
    DESC = auto()


async def movie_filter_params(
    filter_by_certification_id: int = Query(default=None),
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
        "filter_by_certification_id": filter_by_certification_id,
        "filter_by_genres_ids": filter_by_genres_ids,
        "filter_by_min_year": filter_by_min_year,
        "filter_by_max_year": filter_by_max_year,
        "filter_by_min_time": filter_by_min_time,
        "filter_by_max_time": filter_by_max_time,
        "filter_by_min_imdb": filter_by_min_imdb,
        "filter_by_max_imdb": filter_by_max_imdb,
        "filter_by_min_price": filter_by_min_price,
        "filter_by_max_price": filter_by_max_price
    }
search_by_

async def movie_search_params(
    search_by_name: str = Query(default=None),
    search_by_description: str = Query(default=None),
    search_by_stars_ids: list[int] = Query(default=None),
    search_by_directors_ids: list[int] = Query(default=None)
) -> dict:
    return {
        "search_by_name": search_by_name,
        "search_by_description": search_by_description,
        "search_by_stars_ids": search_by_stars_ids,
        "search_by_directors_ids": search_by_directors_ids
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
        "name": sort_by_name,
        "year": sort_by_year,
        "time": sort_by_time,
        "imdb": sort_by_imdb,
        "votes": sort_by_votes,
        "meta_score": sort_by_meta_score,
        "gross": sort_by_gross,
        "price": sort_by_price
    }


MovieFilterDep = Annotated[dict, Depends(movie_filter_params)]
MovieSearchDep = Annotated[dict, Depends(movie_search_params)]
MovieSortDep = Annotated[
    dict[str, SortingOrderEnum | None],
    Depends(movie_sort_params)
]
