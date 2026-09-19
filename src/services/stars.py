from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import StarModel
from src.repositories.movies import StarRepository
from src.services import mixins


class StarService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(self, star_repository: StarRepository) -> None:
        self.star_repository = star_repository

    async def get_star_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_stars = await self.star_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_stars,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_stars
            )

            stars = await self.star_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                order_by_columns=[StarModel.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/stars/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "stars": stars,
                "total_stars": total_stars,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with stars"
            )
