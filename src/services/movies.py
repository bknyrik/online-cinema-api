from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import MovieModel
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

    async def get_movie_list(self, db: AsyncSession) -> dict:
        try:
            movies_list = list(
                await self.movie_repository.aget_all(
                    db=db,
                    join_relationships=[
                        "genres",
                        "stars",
                        "directors",
                        "certification"
                    ]
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movies"
            )
        else:
            return {
                "movies": [
                    {
                        "id": movie.id,
                        "uuid": movie.uuid,
                        "name": movie.name,
                        "year": movie.year,
                        "time": movie.time,
                        "imdb": movie.imdb,
                        "votes": movie.votes,
                        "meta_score": movie.meta_score,
                        "gross": movie.gross,
                        "description": movie.description,
                        "price": movie.price,
                        "certification": movie.certification.name,
                        "genres": [genre.name for genre in movie.genres],
                        "stars": [star.name for star in movie.stars],
                        "directors": [director.name for director in movie.directors],
                    }
                    for movie in movies_list
                ]
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
            movie = await self.movie_repository.aget_by_name_year_time(
                db=db,
                name=data["name"],
                year=data["year"],
                time=data["time"]
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
