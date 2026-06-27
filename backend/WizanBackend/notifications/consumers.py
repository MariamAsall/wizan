# notifications/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # التأكد من وجود user وحمايته من الـ KeyError
        self.user = self.scope.get("user", None)

        # إذا كان المستخدم غير مسجل أو مجهول، ارفض الاتصال
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        # الانضمام للمجموعة الخاصة بالمستخدم
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # دالة استقبال الحدث وإرساله للفرونت إند
    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))