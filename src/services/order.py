from decimal import Decimal

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from src.repositories import order as repositories
from src.repositories.cinema import MovieRepository

from src.database.models import order as models
from src.database.models.accounts import UserModel
from src.database.models.cinema import MovieModel
from src.services import mixins


class OrderService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.FilterItemsMixin,
    mixins.UserPermissionsMixin
):

    def __init__(self) -> None:
        self.model_type = models.OrderModel
        self.order_repository = repositories.OrderRepository()
        self.order_item_repository = repositories.OrderItemRepository()
        self.movie_repository = MovieRepository()

    async def get_order_list(
        self,
        db: AsyncSession,
        query_params: dict
    ) -> dict:
        try:
            pagination_data, filter_data = (
                self.get_pagination_data(query_params),
                self.get_filter_data(query_params),
            )
            limit, offset = self.get_limit_offset(pagination_data)
            expressions = self.get_filter_expressions(filter_data)

            total_orders = await self.order_repository.acount(
                db=db,
                expressions=expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_orders,
                per_page=pagination_data["per_page"]
            )

            orders = await self.order_repository.aget_all_with_order_items_count(
                db=db,
                expressions=expressions,
                limit=limit,
                offset=offset
            )
            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/shopping/orders/",
                query_params=query_params,
                page=pagination_data["page"],
                total_pages=total_pages
            )

            return {
                "orders": orders,
                "total_orders": total_orders,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with orders"
            )

    async def get_order_detail(
        self,
        db: AsyncSession,
        order_id: int,
        current_user: UserModel
    ) -> models.OrderModel:
        try:
            order = await self.order_repository.aget_by_id(
                db=db,
                id_=order_id,
                load_relationships=[
                    joinedload(self.model_type.order_items)
                    .joinedload(models.OrderItemModel.movie)
                    .joinedload(MovieModel.genres)
                ]
            )

            self.validate_item_by_id_not_found(
                item=order,
                id_=order_id,
                item_type="Order"
            )

            self.belongs_to_user_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=order,
                child_object_type="Order"
            )

            return order
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting order"
            )

    async def get_current_user_order_list(
        self,
        db: AsyncSession,
        query_params: dict,
        current_user: UserModel
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(query_params)
            expressions = [self.model_type.user_id == current_user.id]
            total_orders = await self.order_repository.acount(
                db=db,
                expressions=expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_orders,
                per_page=query_params["per_page"]
            )

            orders = list(
                await self.order_repository.aget_all_with_order_items_count(
                    db=db,
                    expressions=expressions,
                    limit=limit,
                    offset=offset
                )
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/shopping/orders/me/content/",
                query_params=query_params,
                page=query_params["page"],
                total_pages=total_pages
            )
            return {
                "orders": orders,
                "total_orders": total_orders,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting current user orders"
            )

    async def create_order(
        self,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.OrderModel:
        try:
            if not current_user.cart.cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User can't create an order from the empty cart"
                )

            order = await self.order_repository.acreate(
                db=db,
                data={
                    "user_id": current_user.id,
                    "total_amount": Decimal("0")
                }
            )

            movies: list[MovieModel] = [
                cart_item.movie for cart_item in current_user.cart.cart_items
            ]

            for movie in movies:
                order_item = await self.order_item_repository.acreate(
                    db=db,
                    data={
                        "movie_id": movie.id,
                        "order_id": order.id,
                        "price_at_order": movie.price
                    }
                )
                order.total_amount += order_item.price_at_order

            await db.commit()

            order = await self.order_repository.aget_by_id(
                db=db,
                id_=order.id,
                load_relationships=[
                    joinedload(self.model_type.order_items)
                    .joinedload(models.OrderItemModel.movie)
                    .joinedload(MovieModel.genres)
                ]
            )

            return order
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while order creation"
            )
