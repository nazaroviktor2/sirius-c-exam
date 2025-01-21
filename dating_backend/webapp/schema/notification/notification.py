from pydantic import BaseModel


class NotificationResponse(BaseModel):
    is_notified: bool
