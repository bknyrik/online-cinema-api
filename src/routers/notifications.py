from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import database, authentication, pagination
from src.database.models.accounts import UserModel
from src.services.notifications import NotificationService


router = APIRouter()


@router.get("/")
async def get_notification_list(
    pagination_data: pagination.PaginationDep,
    db: AsyncSession = Depends(database.get_db),
    notification_service: NotificationService = Depends(NotificationService),
    current_user: UserModel = Depends(authentication.get_current_user),
) -> dict:
    return await notification_service.get_notification_list(
        db=db,
        pagination_data=pagination_data,
        current_user=current_user
    )
