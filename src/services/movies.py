from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import MovieModel
from src.dependencies.movies import SortingOrderEnum
from src.repositories import movies
from src.services import mixins


class MovieService(mixins.PaginationLimitOffsetMixin):

    def __init__(
        self,
        movie_repository: movies.MovieRepository,
        genre_repository: movies.GenreRepository,
        star_repository: movies.StarRepository,
        director_repository: movies.DirectorRepository,
        certification_repository: movies.CertificationRepository
    ) -> None:
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.star_repository = star_repository
        self.director_repository = director_repository
        self.certification_repository = certification_repository

    @staticmethod
    def validate_all_ids_exist(
        ids: list[int],
        items: Sequence,
        item_type: str
    ) -> None:
        items_ids = tuple(item.id for item in items)

        for id_ in ids:
            if id_ not in items_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{item_type} with id {id_} not found"
                )

    @staticmethod
    def get_sort_columns(
        sort_data: dict[str, SortingOrderEnum | None]
    ) -> list[InstrumentedAttribute | UnaryExpression]:
        sort_data = {
            key.replace("sort_by_", ""): value
            for key, value in sort_data.items()
        }
        sort_columns = []

        for name, order in sort_data.items():
            if order is not None:
                column = getattr(MovieModel, name)
                sort_columns.append(
                    column if order == SortingOrderEnum.ASC else column.desc()
                )

        return sort_columns

    @staticmethod
    def get_search_expressions(search_data: dict) -> list[ColumnElement[bool]]:
        search_data = {
            key.replace("search_by_", ""): value
            for key, value in search_data.items()
        }

        search_expressions = []

        for name, value in search_data.items():
            if value is not None:
                if isinstance(value, str):
                    search_expressions.append(
                        getattr(MovieModel, name).icontains(value)
                    )

                if name.endswith("_ids"):
                    column = getattr(MovieModel, name.replace("_ids", ""))
                    child_model = column.prop.argument
                    search_expressions.append(
                        column.any(child_model.id.in_(value))
                    )

        return search_expressions

    @staticmethod
    def _get_min_max_filter_expressions(
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
            column = getattr(MovieModel, min_key.replace("min_", ""))
            min_value, max_value = filter_data[min_key], filter_data[max_key]

            if min_value is not None and max_value is not None:
                expressions.append(column.between(min_value, max_value))

            elif min_value is not None:
                expressions.append(column >= min_value)

            elif max_value is not None:
                expressions.append(column <= max_value)

        return expressions

    @staticmethod
    def _get_single_id_expressions(
        filter_data: dict
    ) -> list[ColumnElement[bool]]:
        return [
            getattr(MovieModel, name) == filter_data[name]
            for name, value in filter_data.items()
            if name.endswith("_id") and value is not None
        ]

    @staticmethod
    def _get_multiple_ids_expressions(
        filter_data: dict
    ) -> list[ColumnElement[bool]]:
        expressions = []

        for name, value in filter_data.items():
            if name.endswith("_ids") and value is not None:
                column = getattr(MovieModel, name.replace("_ids", ""))
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

    async def get_movie_list(
        self,
        db: AsyncSession,
        pagination_data: dict,
        filter_data: dict,
        search_data: dict,
        sort_data: dict[str, SortingOrderEnum | None]
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_movies = await self.movie_repository.acount(db)
            total_pages = self.get_total_pages(
                total_movies,
                pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_movies
            )

            filter_expressions = self.get_filter_expressions(filter_data)
            search_expressions = self.get_search_expressions(search_data)
            sort_columns = (
                self.get_sort_columns(sort_data)
                if any(sort_data.values()) else [MovieModel.id]
            )

            movies_list = list(
                await self.movie_repository.aget_all(
                    db=db,
                    join_relationships=[
                        "genres",
                        "stars",
                        "directors",
                        "certification"
                    ],
                    offset=offset,
                    limit=limit,
                    expressions=filter_expressions + search_expressions,
                    order_by_columns=sort_columns
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movies"
            )
        else:
            prev_page, next_page = (
                self.get_prev_next_urls_pages(
                    "/api/movies/",
                    page=pagination_data["page"],
                    total_pages=total_pages,
                    query_params={
                        **pagination_data,
                        **filter_data,
                        **search_data,
                        **sort_data
                    }
                )
            )
            return {
                "movies": movies_list,
                "total_movies": total_movies,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }

    async def get_detail_movie(self, db: AsyncSession, movie_id: int) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id,
                join_relationships=[
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                ]
            )

            if not movie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Movie not found"
                )

            return movie
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting movie"
            )

    async def create_movie(self, db: AsyncSession, data: dict) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by(
                db=db,
                expressions=[
                    MovieModel.name == data["name"],
                    MovieModel.year == data["year"],
                    MovieModel.time == data["time"]
                ]
            )

            if movie:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Move with this name, year and time exists"
                )

            genres_ids = data.pop("genres")
            stars_ids = data.pop("stars")
            directors_ids = data.pop("directors")

            genres = await self.genre_repository.aget_by_ids(db, genres_ids)
            self.validate_all_ids_exist(genres_ids, genres, "Genre")

            stars = await self.star_repository.aget_by_ids(db, stars_ids)
            self.validate_all_ids_exist(stars_ids, stars, "Star")

            directors = await self.director_repository.aget_by_ids(db, directors_ids)
            self.validate_all_ids_exist(directors_ids, directors, "Director")

            data["certification_id"] = data.pop("certification")

            certification = await self.certification_repository.aget_by_id(
                db=db,
                id_=data["certification_id"]
            )

            if not certification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Certification with id {data['certification_id']} not found"
                )

            created_movie = await self.movie_repository.acreate(
                db=db,
                data=data
            )

            created_movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=created_movie.id,
                join_relationships=[
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                ]
            )

            created_movie.genres = genres
            created_movie.stars = stars
            created_movie.directors = directors

            await db.commit()
            return created_movie
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating movie"
            )

    async def update_movie(
        self,
        db: AsyncSession,
        movie_id: int,
        data: dict
    ) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id,
                join_relationships=[
                    "certification",
                    "genres",
                    "stars",
                    "directors"
                ]
            )

            if not movie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie with id {movie_id} not found"
                )

            if data.get("name") and data.get("year") and data.get("time"):
                another_movie = await self.movie_repository.aget_by(
                    db=db,
                    expressions=[
                        MovieModel.name == data["name"],
                        MovieModel.year == data["year"],
                        MovieModel.time == data["time"]
                    ]
                )

                if (
                    another_movie
                    and another_movie.name != movie.name
                    and another_movie.year != movie.year
                    and another_movie.time != movie.time
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Movie with this name, year and time exists"
                    )

            await self.movie_repository.aupdate(
                db=db,
                instance=movie,
                data=data
            )
            await db.commit()
            return movie
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating movie"
            )

    async def delete_movie(self, db: AsyncSession, movie_id: int) -> None:
        try:
            movie = await self.movie_repository.adelete_by_id(
                db=db,
                id_=movie_id
            )

            if not movie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie with id {movie_id} not found"
                )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie deletion"
            )
