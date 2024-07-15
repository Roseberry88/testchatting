import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName, 
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "chat_message")
        username = text_data_json["username"]

        if message_type == "chat_message":
            message = text_data_json["message"]
            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "sendMessage",
                    "message": message,
                    "username": username,
                }
            )
        elif message_type == "file_upload_request":
            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "file_upload_start",
                    "username": username,
                }
            )
        elif message_type == "file_upload_complete":
            file_name = text_data_json["file_name"]
            file_url = text_data_json["file_url"]
            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "file_upload_end",
                    "username": username,
                    "file_name": file_name,
                    "file_url": file_url,
                }
            )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": message,
            "username": username
        }))

    async def file_upload_start(self, event):
        username = event["username"]
        await self.send(text_data=json.dumps({
            "type": "file_upload_start",
            "username": username
        }))

    async def file_upload_end(self, event):
        username = event["username"]
        file_name = event["file_name"]
        file_url = event["file_url"]
        await self.send(text_data=json.dumps({
            "type": "file_upload_end",
            "username": username,
            "file_name": file_name,
            "file_url": file_url
        }))