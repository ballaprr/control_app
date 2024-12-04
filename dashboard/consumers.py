from channels.generic.websocket import AsyncJsonWebsocketConsumer

class LegendConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Add the WebSocket connection to a group
        await self.channel_layer.group_add("legend_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard("legend_updates", self.channel_name)

    async def send_update(self, event):
        # Send updated data to the WebSocket
        await self.send_json(event["data"])
