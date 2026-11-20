from fastapi import APIRouter, status

from src.dependencies import database, authentication, services
from src.schemas import notifications as schemas


router = APIRouter()


@router.get(
    "/",
    response_model=schemas.NotificationListResponseSchema
)
async def get_notification_list(
    query_params: schemas.NotificationListQuery,
    db: database.AsyncSessionDep,
    notification_service: services.NotificationServiceDep,
    current_user: authentication.CurrentUserDep,
) -> dict:
    return await notification_service.get_notification_list(
        db=db,
        query_params=query_params.model_dump(),
        current_user=current_user
    )


@router.delete(
    "/delete/{notification_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_notification(
    notification_id: int,
    db: database.AsyncSessionDep,
    notification_service: services.NotificationServiceDep,
    current_user: authentication.CurrentUserDep
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
    db: database.AsyncSessionDep,
    notification_service: services.NotificationServiceDep,
    current_user: authentication.CurrentUserDep
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
    db: database.AsyncSessionDep,
    notification_service: services.NotificationServiceDep,
    current_user: authentication.CurrentUserDep
) -> None:
    return await notification_service.mark_notifications_as_read(
        db=db,
        current_user=current_user
    )
