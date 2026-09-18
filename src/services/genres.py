from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.movies import GenreRepository
from src.services.mixins import PaginationLimitOffsetMixin


class GenreService(PaginationLimitOffsetMixin):

    def __init__(self, genre_repository: GenreRepository) -> None:
        self.genre_repository = genre_repository

    async def get_genre_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            total_genres = await self.genre_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_genres,
                per_page=pagination_data["per_page"]
            )
            limit, offset = self.get_limit_offset(pagination_data)

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_genres
            )

            genres = list(
                await self.genre_repository.aget_all(
                    db=db,
                    offset=offset,
                    limit=limit,
                )
            )
            count_movies = await self.genre_repository.acount_movies(db)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with genres"
            )
        else:
            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/genres/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )
            genres = [
                {"id": genre.id, "name": genre.name, "movies": count}
                for genre, count in zip(genres, count_movies)
            ]
            return {
                "genres": genres,
                "total_genres": total_genres,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
