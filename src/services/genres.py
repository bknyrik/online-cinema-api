from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.movies import GenreRepository


class GenreService:

    def __init__(self, genre_repository: GenreRepository) -> None:
        self.genre_repository = genre_repository

    async def get_genre_list(self, db: AsyncSession) -> dict:
        try:
            genres = list(await self.genre_repository.aget_all(db))
            return {
                "genres": genres
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with genres"
            )
