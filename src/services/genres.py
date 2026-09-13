import math

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.movies import GenreRepository


class GenreService:

    def __init__(self, genre_repository: GenreRepository) -> None:
        self.genre_repository = genre_repository

    async def get_genre_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            total_genres = await self.genre_repository.acount(db)
            page, per_page = (
                pagination_data["page"],
                pagination_data["per_page"]
            )
            total_pages = math.ceil(total_genres / per_page)
            offset = per_page * (page - 1)

            genres = list(
                await self.genre_repository.aget_all(
                    db=db,
                    offset=offset,
                    limit=per_page,
                    join_relationships=["movies"]
                )
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with genres"
            )
        else:
            return {
                "genres": genres,
                "total_genres": total_genres,
                "total_pages": total_pages,
                "prev": (
                    f"api/genres/?per_page={per_page}&page={page - 1}"
                    if page > 1 else None
                ),
                "next": (
                    f"api/genres/?per_page={per_page}&page={page + 1}"
                    if page < total_pages else None
                )
            }
