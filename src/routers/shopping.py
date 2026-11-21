from fastapi import APIRouter, status

from src.dependencies import authentication, database, services
from src.database.models import shopping as models
from src.schemas import shopping as schemas, pagination


router = APIRouter()


@router.get("/carts/", response_model=schemas.CartListResponseSchema)
async def get_cart_list(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    pagination_data: pagination.PaginationQuery
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
    cart_service: services.CartServiceDep
) -> models.CartModel:
    return await cart_service.get_cart_detail(
        db=db,
        cart_id=cart_id
    )


@router.get(
    "/carts/me/",
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
