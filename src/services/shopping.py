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

    async def get_cart_list(self, db: AsyncSession) -> dict:
        try:
            carts = await self.cart_repository.aget_all_with_count_cart_items(
                db=db
            )
            return {
                "carts": carts
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
