from typing import Annotated

from fastapi import Depends, Query


async def movie_filter_parameters(
    genres_ids: list[int] = Query(default=None),
    min_year: int = Query(default=None),
    max_year: int = Query(default=None),
    min_time: int = Query(default=None),
    max_time: int = Query(default=None),
    min_imdb: int = Query(default=None),
    max_imdb: int = Query(default=None),
    min_price: int = Query(default=None),
    max_price: int = Query(default=None)
) -> dict:
    return {
        "genres_ids": genres_ids,
        "min_year": min_year,
        "max_year": max_year,
        "min_time": min_time,
        "max_time": max_time,
        "min_imdb": min_imdb,
        "max_imdb": max_imdb,
        "min_price": min_price,
        "max_price": max_price
    }


async def movie_search_params(
    name: str = Query(default=None),
    description: str = Query(default=None),
    stars_ids: list[int] = Query(default=None),
    directors_ids: list[int] = Query(default=None)
) -> dict:
    return {
        "name": name,
        "description": description,
        "stars_ids": stars_ids,
        "directors_ids": directors_ids
    }


MovieFilterDep = Annotated[dict, Depends(movie_filter_parameters)]
MovieSearchDep = Annotated[dict, Depends(movie_search_params)]
