import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def websocket_application(scope, receive, send):
    # 占位 WebSocket 路由，可后续替换为实际路由
    pass

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": URLRouter([path("ws/", websocket_application)]),
})