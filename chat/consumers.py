# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import get_user, login, logout
from channels.db import database_sync_to_async
from .models import ChatRoom, RoomMessage, DirectMessage
from datetime import datetime
from django.contrib.auth.models import User


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user= self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return False
           
        else: 
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        
            # check if room exists
            room, created= await self.get_or_create_room(self.room_name, self.user)
            
            # add user to room
            await self.add_user_to_room(room, self.user)
            
            # Join room group
            await self.channel_layer.group_add(self.room_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.save_room_message(self.room_name, self.user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name, {"type": "chat_message", "message": message, "sender": self.channel_name, "username": self.user.username}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        if self.channel_name != event["sender"]:
            await self.send(text_data=json.dumps(
                {"message": message, 
                 "username": event["username"]
                }))
        else:
            pass
            # stor message into chat room messages table

     # --- DATABASE HELPERS ---    
    @database_sync_to_async
    def get_or_create_room(self, room_name, user):
        room, created= ChatRoom.objects.get_or_create(name=room_name, defaults={'creator': user})
        return room, created

    @database_sync_to_async
    def add_user_to_room(self, room, user):
        room.members.add(user)
        room.save()

    @database_sync_to_async
    def save_room_message(self, room_name, user, message):
        room = ChatRoom.objects.get(name=room_name)
        RoomMessage.objects.create(
            room=room, 
            sender=user, 
            content=message,
            timestamp=datetime.now())


class PrivateMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user= self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return False
           
        else: 
            self.recipient_name = self.scope["url_route"]["kwargs"]["recipient_name"]
        
            # Generate a deterministic group name
            users = sorted([self.user.username, self.recipient_name])
            self.group_name = f"private_{users[0]}_{users[1]}"
            print(self.group_name)
            # Join room group
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # save message to database
        self.recipient = await database_sync_to_async(User.objects.get)(username=self.recipient_name)
        await self.save_private_message( self.user, self.recipient, message)

        await self.channel_layer.group_send(
            self.group_name, {"type": "private_message", "message": message, "sender": self.channel_name, "username": self.user.username}
        )


        # Notify the recipient that they got a new message
        notification_group = f"notifications_{self.recipient_name}"
        await self.channel_layer.group_send(
            notification_group,
            {
                "type": "notify",
                "content": {
                    "type": "new_message",
                    "from": self.user.username,
                    "text": message,
                },
            },
        )

    # Receive message from sender
    async def private_message(self, event):
        message = event["message"]
        if self.channel_name != event["sender"]:
            await self.send(text_data=json.dumps(
                {"message": message, 
                 "username": event["username"]
                }))
        else:
            pass

    @database_sync_to_async
    def save_private_message(self, sender, recipient, message):
        DirectMessage.objects.create(
            recipient=recipient,
            sender=sender,
            content=message,
            timestamp=datetime.now())
            
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return
        else:
            # Each user has their own notification group
            self.group_name = f"notifications_{self.user.username}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
 
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Called when a notification is sent to this user's group
    async def notify(self, event):
        await self.send(text_data=json.dumps(event["content"]))