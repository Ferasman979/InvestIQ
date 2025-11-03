from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Notification(BaseModel):
    notification_id: str
    user_id: str
    message: str
    read: bool = False
    created_at: Optional[datetime] = datetime.now()
