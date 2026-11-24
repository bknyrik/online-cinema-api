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
    mixins.FilterItemsMixin
):

    def __init__(self) -> None:
        self.model_type = models.OrderModel
        self.order_repository = repositories.OrderRepository()
        self.order_item_repository = repositories.OrderItemRepository()
        self.movie_repository = MovieRepository()

    async def create_order(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel
    ) -> dict:
        try:
            order = await self.order_repository.acreate(
                db=db,
                data={
                    "user_id": current_user.id,
                    "total_amount": Decimal("0")
                }
            )

            movie_ids = data["movies"]

            for movie_id in movie_ids:
                movie = await self.movie_repository.aget_by_id(
                    db=db,
                    id_=movie_id
                )
                self.validate_item_by_id_not_found(
                    item=movie,
                    id_=movie_id,
                    item_type="Movie"
                )
                order_item = await self.order_item_repository.acreate(
                    db=db,
                    data={
                        "movie_id": movie_id,
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

            return {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "created_at": order.created_at,
                "movies": [
                    order_item.movie for order_item in order.order_items
                ],
                "total_amount": order.total_amount
            }
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while order creation"
            )
