from src.repositories.base import AsyncBaseRepository
from src.database.models.notifications import NotificationModel


class NotificationRepository(AsyncBaseRepository[NotificationModel]):

    def __init__(self) -> None:
        super().__init__(NotificationModel)
