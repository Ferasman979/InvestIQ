from models.notification_model import Notification
import uuid
from datetime import datetime

def send_notification(user_id: str, message: str):
    notification = Notification(
        notification_id=str(uuid.uuid4()),
        user_id=user_id,
        message=message,
        created_at=datetime.now()
    )
    return notification.dict()
