from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def create_notification(user, title, message, notification_type="info"):
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send_notification",
            "data": {
                "id": notification.id,
                "title": title,
                "message": message,
                "type": notification_type,
            }
        }
    )

    return notification