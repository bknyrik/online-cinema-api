from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import database, authentication
from src.database.models.accounts import UserModel
from src.services.notifications import NotificationService
from src.schemas.notifications import (
    NotificationListResponseSchema,
    NotificationListQuery
)
from src.schemas import pagination


router = APIRouter()


@router.get(
    "/",
    response_model=NotificationListResponseSchema
)
async def get_notification_list(
    query_params: NotificationListQuery,
    db: AsyncSession = Depends(database.get_db),
    notification_service: NotificationService = Depends(NotificationService),
    current_user: UserModel = Depends(authentication.get_current_user),
) -> dict:
    return await notification_service.get_notification_list(
        db=db,
        query_data=query_params.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/delete/{notification_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(database.get_db),
    notification_service: NotificationService = Depends(NotificationService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await notification_service.delete_notification(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )


@router.delete(
    "/delete-all/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_all_notifications(
    db: AsyncSession = Depends(database.get_db),
    notification_service: NotificationService = Depends(NotificationService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await notification_service.delete_all_notifications(
        db=db,
        current_user=current_user
    )


@router.post(
    "/mark-read/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def mark_notifications_as_read(
    db: AsyncSession = Depends(database.get_db),
    notification_service: NotificationService = Depends(NotificationService),
    current_user: UserModel = Depends(authentication.get_current_user)
) -> None:
    return await notification_service.mark_notifications_as_read(
        db=db,
        current_user=current_user
    )
