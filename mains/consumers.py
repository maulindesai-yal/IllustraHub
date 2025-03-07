import json
from channels.generic.websocket import AsyncWebsocketConsumer
from mains.models import Illustration, Bid
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.illustration_id = self.scope['url_route']['kwargs']['illustration_id']
        self.group_name = f'bid_{self.illustration_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        bid_amount = float(data['bid_amount'])
        user = self.scope["user"]

        illustration = await Illustration.objects.aget(id=self.illustration_id)
        highest_bid = await Bid.objects.filter(illustration=illustration).afirst()

        if bid_amount <= (highest_bid.amount if highest_bid else illustration.price):
            return

        new_bid = await Bid.objects.acreate(illustration=illustration, user=user, amount=bid_amount)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'bid_update',
                'bidder': user.username,
                'bid_amount': bid_amount,
                'bid_count': await Bid.objects.filter(illustration=illustration).acount(),
                'timestamp': now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    async def bid_update(self, event):
        await self.send(text_data=json.dumps(event))