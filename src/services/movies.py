import math
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import MovieModel, GenreModel
from src.repositories import movies


class MovieService:

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
    def check_all_ids_exist(
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
    def get_filter_expressions(filter_data: dict) -> list:
        def _get_min_max_expression(
            min_value: int | None,
            max_value: int | None,
            column_name: str
        ):
            if min_value is not None and max_value is not None:
                return (
                    getattr(MovieModel, column_name)
                    .between(
                        min_value,
                        max_value
                    )
                )

            elif min_value is not None:
                return getattr(MovieModel, column_name) >= min_value

            elif max_value is not None:
                return getattr(MovieModel, column_name) <= max_value

            return None

        def _get_ids_expression(
            ids: list[int],
            column_name: str,
            column_type
        ) -> ColumnElement[bool] | None:
            if ids:
                return (
                    getattr(MovieModel, column_name)
                    .any(column_type.id.in_(ids))
                )

            return None

        min_max_columns = ("year", "time", "imdb", "price")
        ids_columns_models = {
            "genres": GenreModel
        }

        min_max_expressions = tuple(
            _get_min_max_expression(
                filter_data[f"min_{column_name}"],
                filter_data[f"max_{column_name}"],
                column_name
            )
            for column_name in min_max_columns
        )
        ids_expressions = tuple(
            _get_ids_expression(
                filter_data[f"{column_name}_ids"],
                column_name,
                model
            )
            for column_name, model in ids_columns_models.items()
        )

        expressions = min_max_expressions + ids_expressions

        return [
            expression for expression in expressions
            if expression is not None
        ]

    async def get_movie_list(
        self,
        db: AsyncSession,
        pagination_data: dict,
        filter_data: dict,
    ) -> dict:
        try:
            page, per_page = (
                pagination_data["page"],
                pagination_data["per_page"]
            )
            total_movies = await self.movie_repository.acount(db)
            total_pages = math.ceil(total_movies / per_page)
            offset = per_page * (page - 1)

            if page > total_pages:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Page not found"
                )

            filter_expressions = self.get_filter_expressions(filter_data)

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
                    limit=per_page,
                    expressions=filter_expressions,
                    order_by_columns=[MovieModel.id]
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movies"
            )
        else:
            prev = (
                f"/api/movies/?per_page={per_page}&page={page - 1}"
                if page > 1 else None
            )
            next_ = (
                f"/api/movies/?per_page={per_page}&page={page + 1}"
                if page < total_pages else None
            )
            return {
                "movies": movies_list,
                "total_movies": total_movies,
                "total_pages": total_pages,
                "prev": prev,
                "next": next_
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
            self.check_all_ids_exist(genres_ids, genres, "Genre")

            stars = await self.star_repository.aget_by_ids(db, stars_ids)
            self.check_all_ids_exist(stars_ids, stars, "Star")

            directors = await self.director_repository.aget_by_ids(db, directors_ids)
            self.check_all_ids_exist(directors_ids, directors, "Director")

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
            filtered_data = dict(
                filter(lambda item: item[1] is not None, data.items())
            )

            if not movie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie with id {movie_id} not found"
                )

            if (
                filtered_data.get("name")
                and filtered_data.get("year")
                and filtered_data.get("time")
            ):
                another_movie = await self.movie_repository.aget_by(
                    db=db,
                    expressions=[
                        MovieModel.name == filtered_data["name"],
                        MovieModel.year == filtered_data["year"],
                        MovieModel.time == filtered_data["time"]
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
                data=filtered_data
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
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id
            )

            if not movie:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie with id {movie_id} not found"
                )

            await self.movie_repository.adelete(db, movie)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
