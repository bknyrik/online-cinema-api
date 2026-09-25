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

    async def get_star_detail(
        self,
        db: AsyncSession,
        star_id: int
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(star, star_id, "Star")

            return star
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the star"
            )

    async def create_star(
        self,
        db: AsyncSession,
        data: dict
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by(
                db=db,
                expressions=[StarModel.name == data["name"]]
            )

            self.validate_item_by_attrs_exists(
                item=star,
                attrs=data,
                item_type="Star"
            )

            star = await self.star_repository.acreate(
                db=db,
                data=data
            )

            await db.commit()
            return star
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star creation"
            )

    async def update_star(
        self,
        db: AsyncSession,
        data: dict,
        star_id: int
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(
                item=star,
                id_=star_id,
                item_type="Star"
            )

            another_star = await self.star_repository.aget_by(
                db=db,
                expressions=[StarModel.name == data["name"]]
            )

            self.validate_item_by_attrs_with_another_item_exists(
                item=star,
                another_item=another_star,
                attrs=data,
                item_type="Star"
            )

            await self.star_repository.aupdate(db, star, data)
            await db.commit()
            return star
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star updating"
            )

    async def delete_star(
        self,
        db: AsyncSession,
        star_id: int
    ) -> None:
        try:
            star = await self.star_repository.adelete_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(star, star_id, "Star")

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star deletion"
            )
