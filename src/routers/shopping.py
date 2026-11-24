from fastapi import APIRouter, status

from src.dependencies import authentication, database, services
from src.database.models import shopping as models
from src.database.models.order import OrderModel
from src.schemas.order import (
    OrderDetailResponseSchema,
    CurrentUserOrderDetailResponseSchema
)
from src.schemas import shopping as schemas, pagination


router = APIRouter()


@router.get("/carts/", response_model=schemas.CartListResponseSchema)
async def get_cart_list(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    pagination_data: pagination.PaginationQuery,
    current_user: authentication.CurrentAdminDep
) -> dict:
    return await cart_service.get_cart_list(
        db=db,
        pagination_data=pagination_data.model_dump()
    )


@router.get(
    "/carts/{cart_id}/",
    response_model=schemas.CartDetailResponseSchema
)
async def get_cart_detail(
    cart_id: int,
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    current_user: authentication.CurrentAdminDep
) -> models.CartModel:
    return await cart_service.get_cart_detail(
        db=db,
        cart_id=cart_id
    )


@router.get(
    "/carts/me/content/",
    response_model=schemas.CurrentUserCartDetailResponseSchema
)
async def get_current_user_cart(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    current_user: authentication.CurrentUserDep
) -> models.CartModel:
    return await cart_service.get_current_user_cart(
        db=db,
        current_user=current_user
    )


@router.delete("/carts/me/clear/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_current_user_cart(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    current_user: authentication.CurrentUserDep
) -> None:
    return await cart_service.clear_current_user_cart(
        db=db,
        current_user=current_user
    )


@router.post(
    "/cart_items/",
    response_model=schemas.CartItemDetailSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_cart_item(
    db: database.AsyncSessionDep,
    data: schemas.CartItemCreateRequestSchema,
    cart_item_service: services.CartItemServiceDep,
    current_user: authentication.CurrentUserDep
) -> models.CartItemModel:
    return await cart_item_service.create_cart_item(
        db=db,
        data=data.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/cart_items/{cart_item_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_cart_item(
    cart_item_id: int,
    db: database.AsyncSessionDep,
    cart_item_service: services.CartItemServiceDep,
    current_user: authentication.CurrentUserDep
) -> None:
    return await cart_item_service.delete_cart_item(
        db=db,
        cart_item_id=cart_item_id,
        current_user=current_user
    )


@router.get(
    "/orders/me/content/",
    response_model=list[CurrentUserOrderDetailResponseSchema],
)
async def get_current_user_order_list(
    db: database.AsyncSessionDep,
    order_service: services.OrderServiceDep,
    current_user: authentication.CurrentUserDep
) -> list[OrderModel]:
    return await order_service.get_current_user_orders(
        db=db,
        current_user=current_user
    )


@router.post(
    "/orders/",
    response_model=OrderDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    db: database.AsyncSessionDep,
    order_service: services.OrderServiceDep,
    current_user: authentication.CurrentUserDep
) -> OrderModel:
    return await order_service.create_order(
        db=db,
        current_user=current_user
    )
