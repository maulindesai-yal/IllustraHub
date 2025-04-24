from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/illustration/(?P<illustration_id>\w+)/$', consumers.IllustrationConsumer.as_asgi()),
]