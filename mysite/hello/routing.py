from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/message/(?P<key>\w+)/$', consumers.EchoConsumer.as_asgi()),
]