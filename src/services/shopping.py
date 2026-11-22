from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models import shopping as models
from src.database.models.accounts import UserModel
from src.database.models.cinema import MovieModel
from src.repositories import shopping as repositories
from src.services import mixins


class CartService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(self) -> None:
        self.model_type = models.CartModel
        self.cart_repository = repositories.CartRepository()
        self.cart_item_repository = repositories.CartItemRepository()

    async def get_cart_list(
        self,
        db: AsyncSession,
        pagination_data: dict
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)

            total_carts = await self.cart_repository.acount(
                db=db
            )
            total_pages = self.get_total_pages(total_carts, pagination_data["per_page"])

            carts = await self.cart_repository.aget_all_with_count_cart_items(
                db=db,
                limit=limit,
                offset=offset
            )
            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/shopping/carts/",
                page=pagination_data["page"],
                query_params=pagination_data,
                total_pages=total_pages
            )
            return {
                "carts": carts,
                "total_carts": total_carts,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with carts"
            )

    async def get_cart_detail(
        self,
        db: AsyncSession,
        cart_id: int
    ) -> models.CartModel:
        try:
            cart = await self.cart_repository.aget_by(
                db=db,
                expressions=[self.model_type.id == cart_id],
                load_relationships=[
                    joinedload(self.model_type.cart_items)
                    .joinedload(models.CartItemModel.movie)
                    .joinedload(MovieModel.genres),
                ]
            )

            self.validate_item_by_id_not_found(
                item=cart,
                item_type="Cart",
                id_=cart_id
            )

            return cart
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting cart"
            )

    async def get_current_user_cart(
        self,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.CartModel:
        try:
            cart = await self.cart_repository.aget_by(
                db=db,
                expressions=[self.model_type.user_id == current_user.id],
                load_relationships=[
                    joinedload(self.model_type.cart_items)
                    .joinedload(models.CartItemModel.movie)
                    .joinedload(MovieModel.genres),
                ]
            )
            return cart
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting current user cart"
            )

    async def clear_current_user_cart(
        self,
        db: AsyncSession,
        current_user: UserModel
    ) -> None:
        try:
            cart = await self.cart_repository.aget_by(
                db=db,
                expressions=[self.model_type.user_id == current_user.id],
                load_relationships=[
                    joinedload(self.model_type.cart_items)
                ]
            )
            cart.cart_items.clear()
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while cleaning current user cart"
            )


class CartItemService(mixins.ModelItemsMixin):

    def __init__(self) -> None:
        self.model_type = models.CartItemModel
        self.cart_item_repository = repositories.CartItemRepository()

    async def create_cart_item(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel
    ) -> models.CartItemModel:
        try:
            cart_item = await self.cart_item_repository.acreate(
                db=db,
                data=data | {"cart_id": current_user.cart.id}
            )

            await db.commit()
            await db.refresh(cart_item)

            cart_item = await self.cart_item_repository.aget_by_id(
                db=db,
                id_=cart_item.id,
                load_relationships=[
                    joinedload(self.model_type.movie)
                    .joinedload(MovieModel.genres)
                ]
            )

            return cart_item
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while adding movie to cart"
            )
