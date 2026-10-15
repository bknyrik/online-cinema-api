from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationDetailSchema(BaseModel):
    id: int
    created_at: datetime
    is_read: bool
    text: str


class NotificationListResponseSchema(BaseModel):
    notifications: list[NotificationDetailSchema]
    total_notifications: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)
