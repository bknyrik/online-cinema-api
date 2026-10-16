from typing import Annotated
from datetime import datetime

from fastapi import Query
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


class NotificationFilterParams(BaseModel):
    user_id: int | None = None
    is_read: bool | None = None


NotificationFilterQuery = Annotated[NotificationFilterParams, Query()]
