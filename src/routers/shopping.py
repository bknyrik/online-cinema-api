from fastapi import APIRouter

from src.dependencies import authentication, database, services
from src.database.models import shopping as models
from src.schemas import shopping as schemas


router = APIRouter()


@router.get("/carts/me/", response_model=schemas.CartDetailResponseSchema)
async def get_current_user_cart(
    db: database.AsyncSessionDep,
    cart_service: services.CartServiceDep,
    current_user: authentication.CurrentUserDep
) -> models.CartModel:
    return await cart_service.get_cart_detail(
        db=db,
        current_user=current_user
    )
