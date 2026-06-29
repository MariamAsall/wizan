"""
ASGI config for WizanBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""
# اسم_مشروعك/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
import jwt
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # استبدل core باسم مجلد مشروعك الأساسي

# 1. كود الـ Middleware لقراءة التوكن وحقن الـ user في الـ scope
@database_sync_to_async
def get_user_from_token(token_string):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # فك تشفير التوكن (SimpleJWT الافتراضي يستخدم SECRET_KEY للمشروع)
        payload = jwt.decode(token_string, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(id=payload['user_id'])
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

# 2. استيراد مسارات الـ Routing الخاصة بالإشعارات
from notifications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware( # هنا قمنا بحل المشكلة وحقن الـ user
        URLRouter(
            websocket_urlpatterns
        )
    ),
})