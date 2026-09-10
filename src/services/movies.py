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

    async def get_detail_movie(self, db: AsyncSession, movie_id: int) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id,
                join_relationships=(
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                )
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

            genres = await self.genre_repository.aget_by_ids(db, data.pop("genres"))
            stars = await self.star_repository.aget_by_ids(db, data.pop("stars"))
            directors = await self.director_repository.aget_by_ids(db, data.pop("directors"))
            data["certification_id"] = data.pop("certification")

            created_movie = await self.movie_repository.acreate(
                db=db,
                data=data
            )

            created_movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=created_movie.id,
                join_relationships=(
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                )
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
