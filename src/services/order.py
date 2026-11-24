from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories import order as repositories
from src.repositories.cinema import MovieRepository

from src.database.models import order as models
from src.database.models.accounts import UserModel
from src.services import mixins


class OrderService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
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
    ) -> models.OrderModel:
        try:
            order = await self.order_repository.acreate(
                db=db,
                data={"user_id": current_user.id}
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
                await self.order_item_repository.acreate(
                    db=db,
                    data={
                        "movie_id": movie_id,
                        "order_id": order.id,
                        "price_at_order": movie.price
                    }
                )

            await db.commit()
            await db.refresh(order, ("order_items",))
            return order
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while order creation"
            )
