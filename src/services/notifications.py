from src.services import mixins
from src.database.models.notifications import NotificationModel
from src.repositories.notifications import NotificationRepository


class NotificationService(
    mixins.PaginationLimitOffsetMixin,
):

    def __init__(self) -> None:
        self.model_type = NotificationModel
        self.notification_repository = NotificationRepository()

