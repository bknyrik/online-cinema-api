from datetime import datetime

from pydantic import BaseModel


class NotificationDetailSchema(BaseModel):
    id: int
    created_at: datetime
    is_read: bool
    text: str
