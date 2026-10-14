from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.database.models.notifications import NotificationModel
from src.database.models.accounts import UserModel
from src.repositories.notifications import NotificationRepository


class NotificationService(
    mixins.PaginationLimitOffsetMixin,
    mixins.UserPermissionsMixin,
    mixins.ModelItemsMixin
):

    def __init__(self) -> None:
        self.model_type = NotificationModel
        self.notification_repository = NotificationRepository()

    async def get_notification_list(
        self,
        db: AsyncSession,
        pagination_data: dict,
        current_user: UserModel
    ) -> dict:
        try:
            expressions = [self.model_type.user_id == current_user.id]
            limit, offset = self.get_limit_offset(pagination_data)
            total_notifications = await self.notification_repository.acount(
                db=db,
                expressions=expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_notifications,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_notifications
            )

            notifications = await self.notification_repository.aget_all(
                db=db,
                expressions=expressions,
                limit=limit,
                offset=offset
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/notifications/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "notifications": notifications,
                "total_pages": total_pages,
                "total_notifications": total_notifications,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with notifications"
            )

    async def delete_notification(
        self,
        db: AsyncSession,
        notification_id: int,
        current_user: UserModel
    ) -> None:
        try:
            notification = await self.notification_repository.aget_by_id(
                db=db,
                id_=notification_id
            )

            self.validate_item_by_id_not_found(
                item=notification,
                id_=notification_id,
                item_type="Notification"
            )

            self.belongs_to_user_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=notification,
                child_object_type="Notification"
            )

            await self.notification_repository.adelete(db, notification)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while notification deletion"
            )
