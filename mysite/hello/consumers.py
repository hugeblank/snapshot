from functools import cache
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User, AnonymousUser

from . import models

class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if (self.user != None and self.user != AnonymousUser()):
            key = self.scope['url_route']['kwargs']['key']
            # key sanitization?
            self.room_group_name = key

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close() # Non-users cannot access direct messaging

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Add message to database
        # TODO: Does this work?
        database_sync_to_async(self.save_message)(self.user, message, self.room_group_name)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'direct_message',
                'message': message,
                'username': self.user.username,
                'user_profile_icon': database_sync_to_async(models.UserInfo.objects.get)(user=self.user).image.url
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    def save_message(self, user, message, room):
        instance = models.Message()
        instance.user = user
        instance.message = message
        instance.room = models.MessageRoom.objects.get(key=room)
        instance.save()
        return instance
