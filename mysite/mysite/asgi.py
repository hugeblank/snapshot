import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
import hello.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            hello.routing.websocket_urlpatterns
        )
    ),
})