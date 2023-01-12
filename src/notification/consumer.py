import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .utils import (
    get_group_name, get_user
)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = await get_user(self.scope)

        group = await get_group_name(user, self.scope)
        self.group_name = group.group_name

        await (self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        print("Connected")
        await self.accept()

    async def disconnect(self, close_code):
        await (self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        print("Disconnected")
        await self.close()

    async def receive_json(self, content, **kwargs):
        await asyncio.sleep(0.5)

    async def send_data(self, event):
        await self.send_json(content=event['data'])
