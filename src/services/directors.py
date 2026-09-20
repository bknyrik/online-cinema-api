from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.repositories.movies import DirectorRepository
from src.database.models.movies import DirectorModel


class DirectorService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):
    def __init__(self, director_repository: DirectorRepository) -> None:
        self.director_repository = director_repository

    async def get_director_list(
        self,
        pagination_data: dict,
        db: AsyncSession,
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_directors = await self.director_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_directors,
                per_page=pagination_data["per_page"]
            )

            directors = await self.director_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/directors/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "directors": directors,
                "total_directors": total_directors,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with directors"
            )

    async def get_director_detail(
        self,
        db: AsyncSession,
        director_id: int
    ) -> DirectorModel:
        try:
            director = await self.director_repository.aget_by_id(
                db=db,
                id_=director_id
            )

            self.validate_item_by_id_not_found(
                item=director,
                id_=director_id,
                item_type="Director"
            )

            return director
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the director"
            )
