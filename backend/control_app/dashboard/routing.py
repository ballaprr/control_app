from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/legend/', consumers.LegendConsumer.as_asgi()),
]
