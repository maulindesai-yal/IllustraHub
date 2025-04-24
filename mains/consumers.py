import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Illustration, Bid
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class BiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.illustration_id = self.scope['url_route']['kwargs']['illustration_id']
        self.room_group_name = f'bidding_{self.illustration_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        bid_amount = text_data_json['bid_amount']
        user_id = text_data_json['user_id']

        # Process the bid
        bid = await self.create_bid(user_id, bid_amount)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'bid_message',
                'bid_amount': bid_amount,
                'user_id': user_id,
                'timestamp': bid.timestamp.isoformat()
            }
        )

    async def bid_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'bid_amount': event['bid_amount'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def create_bid(self, user_id, bid_amount):
        user = User.objects.get(id=user_id)
        illustration = Illustration.objects.get(id=self.illustration_id)
        
        # Create new bid
        bid = Bid.objects.create(
            user=user,
            illustration=illustration,
            amount=bid_amount
        )
        
        # Update illustration current price
        illustration.current_price = bid_amount
        illustration.save()
        
        return bid

class IllustrationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.illustration_id = self.scope['url_route']['kwargs']['illustration_id']
        self.room_group_name = f'illustration_{self.illustration_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'update_status':
            status = text_data_json.get('status')
            await self.update_illustration_status(status)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'status_update',
                    'status': status
                }
            )

    async def status_update(self, event):
        status = event['status']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status
        }))

    @database_sync_to_async
    def update_illustration_status(self, status):
        illustration = Illustration.objects.get(id=self.illustration_id)
        illustration.status = status
        illustration.save()