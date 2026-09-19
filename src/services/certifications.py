from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.repositories.movies import CertificationRepository


class CertificationService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(
        self,
        certification_repository: CertificationRepository
    ) -> None:
        self.certification_repository = certification_repository

    async def get_certification_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_certifications = await self.certification_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_certifications,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_items=total_certifications,
                total_pages=total_pages
            )

            certifications = await self.certification_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/certifications/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "certifications": certifications,
                "total_certifications": total_certifications,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "An error occurred while getting"
                    "list with certifications"
                )
            )
