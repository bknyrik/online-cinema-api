from fastapi import APIRouter, status

from src.dependencies import authentication, database, services
from src.database.models import shopping as models
from src.schemas import shopping as schemas


router = APIRouter()


@router.get("/carts/", response_model=schemas.CartListResponseSchema)
async def get_cart_list(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep
) -> dict:
    return await cart_service.get_cart_list(db)


@router.get("/carts/me/", response_model=schemas.CartDetailResponseSchema)
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
