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


class MovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.SearchItemsMixin,
    mixins.SortingItemsMixin,
    mixins.FilterItemsMixin
):

    _model_type = MovieModel

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

    async def get_movie_list(
        self,
        db: AsyncSession,
        pagination_data: dict,
        filter_data: dict,
        search_data: dict,
        sort_data: dict[str, SortingOrderEnum | None]
    ) -> dict:
        try:
            filter_expressions = self.get_filter_expressions(filter_data)
            search_expressions = self.get_search_expressions(search_data)
            sort_columns = (
                self.get_sort_columns(sort_data)
                if any(value is not None for value in sort_data.values())
                else [MovieModel.id]
            )

            limit, offset = self.get_limit_offset(pagination_data)
            total_movies = await self.movie_repository.acount(
                db=db,
                expressions=filter_expressions
            )
            total_pages = self.get_total_pages(
                total_movies,
                pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_movies
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

            self.validate_item_by_id_not_found(
                item=movie,
                id_=movie_id,
                item_type="Movie"
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

            data["genres"] = genres
            data["stars"] = stars
            data["directors"] = directors

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
