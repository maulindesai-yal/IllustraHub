from django.urls import path
from mains.consumers import BidConsumer

websocket_urlpatterns = [
    path("ws/bid/<int:illustration_id>/", BidConsumer.as_asgi()),
]