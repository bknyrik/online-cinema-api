from typing import Annotated

from fastapi import Depends, Query


async def movie_filter_parameters(
    min_year: int = Query(default=None),
    max_year: int = Query(default=None),
    min_time: int = Query(default=None),
    max_time: int = Query(default=None),
    min_imdb: int = Query(default=None),
    imdb_max_rate: int = Query(default=None),
    min_price: int = Query(default=None),
    max_price: int = Query(default=None)
) -> dict:
    return {
        "min_year": min_year,
        "max_year": max_year,
        "min_time": min_time,
        "max_time": max_time,
        "min_imdb": min_imdb,
        "imdb_max_rate": imdb_max_rate,
        "min_price": min_price,
        "max_price": max_price
    }


MovieFilterDep = Annotated[dict, Depends(movie_filter_parameters)]
