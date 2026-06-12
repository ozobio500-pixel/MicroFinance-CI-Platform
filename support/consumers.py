import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group = f"chat_{self.conversation_id}"

        if not await self.can_access_conversation():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        if self.user.is_admin_user:
            await self.channel_layer.group_send(
                self.room_group,
                {"type": "agent_presence", "online": True, "username": self.user.username},
            )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group"):
            if getattr(self, "user", None) and self.user.is_authenticated and self.user.is_admin_user:
                await self.channel_layer.group_send(
                    self.room_group,
                    {"type": "agent_presence", "online": False, "username": self.user.username},
                )
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data or "{}")
        msg_type = data.get("type", "message")

        if msg_type == "typing" and self.user.is_admin_user:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "typing_indicator",
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", False),
                },
            )
            return

        if msg_type != "message":
            return

        content = (data.get("content") or "").strip()
        if not content:
            return

        message = await self.save_message(content)
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "id": message["id"],
                "content": message["content"],
                "sender": message["sender"],
                "created_at": message["created_at"],
            },
        )

    async def chat_message(self, event):
        # Ensure the outgoing payload has type 'message' (frontend expects this)
        payload = dict(event)
        payload.pop("type", None)
        payload = {"type": "message", **payload}
        await self.send(text_data=json.dumps(payload))

    async def typing_indicator(self, event):
        if event["username"] != self.user.username:
            await self.send(text_data=json.dumps({"type": "typing", **event}))

    async def agent_presence(self, event):
        if not self.user.is_client:
            return
        await self.send(
            text_data=json.dumps(
                {
                    "type": "presence",
                    "online": event["online"],
                    "username": event["username"],
                }
            )
        )

    @database_sync_to_async
    def can_access_conversation(self) -> bool:
        try:
            conv = Conversation.objects.get(pk=self.conversation_id)
        except Conversation.DoesNotExist:
            return False
        if self.user.is_client:
            return conv.client_id == self.user.id
        return self.user.is_admin_user

    @database_sync_to_async
    def save_message(self, content: str) -> dict:
        conv = Conversation.objects.get(pk=self.conversation_id)
        msg = Message.objects.create(
            conversation=conv,
            sender=self.user,
            content=content,
        )
        return {
            "id": msg.id,
            "content": msg.content,
            "sender": self.user.username,
            "created_at": msg.created_at.isoformat(),
        }
