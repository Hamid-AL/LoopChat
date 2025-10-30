# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import get_user, login, logout
from channels.db import database_sync_to_async
from .models import ChatRoom, RoomMessage, DirectMessage
from datetime import datetime
from django.contrib.auth.models import User
from users.models import Profile


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
            await self.channel_layer.group_add("online_users", self.channel_name)
            await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("online_users", self.channel_name)
        

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
    ONLINE_USERS = set()

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Each user has their own notification group
        self.group_name = f"notifications_{self.user.username}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        NotificationConsumer.ONLINE_USERS.add(self.user.username)

        # notify this user's friends that its online
        await self.notify_friends_online_status(True)

        await self.accept()

        # Send initial online status of this user's friends to the newly connected client
        await self.send_initial_online_status()
        print('online users', NotificationConsumer.ONLINE_USERS)
 
    async def disconnect(self, close_code):
        # remove user from online users group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if self.user.username in NotificationConsumer.ONLINE_USERS:
            NotificationConsumer.ONLINE_USERS.remove(self.user.username)

        # Notify friends that this user went offline  
        await self.notify_friends_online_status(False)

    async def notify_friends_online_status(self, is_online):
        """Send online/offline status updates to all of the user's friends"""
        friends = await self.get_friends()

        for friend in friends:
            # Use sync_to_async to access the related user field
            friend_username = await self.get_friend_username(friend)
            friend_group = f"notifications_{friend_username}"
            
            online_count = await self.get_online_friends_count(friend)
            await self.channel_layer.group_send(
                friend_group,
                {
                    "type": "notify",
                    "content": {
                        "type": "status_update",
                        "friend": self.user.username,
                        "is_online": is_online,
                        "online_count": online_count,
                    },
                },
            )

    @database_sync_to_async
    def get_friends(self):
        """Return all friends of the current user"""
        try:
            profile = Profile.objects.get(user=self.user)
            # Prefetch the related user data to avoid additional queries
            return list(profile.friends.all().select_related('user'))
        except Profile.DoesNotExist:
            return []

    @database_sync_to_async
    def get_friend_username(self, friend_profile):
        """Get the username from a friend profile"""
        return friend_profile.user.username

    @database_sync_to_async
    def get_online_friends_count(self, profile):
        """Return the number of friends currently online for a given profile"""
        return profile.friends.filter(user__username__in=NotificationConsumer.ONLINE_USERS).count()

    async def send_initial_online_status(self):
        """Send the list/count of currently online friends to the connecting user."""
        friends = await self.get_friends()  # returns list of Profile instances
        # compute online friends usernames (do not call ORM here)
        online_friends = [p.user.username for p in friends if p.user.username in NotificationConsumer.ONLINE_USERS]
        payload = {
            "type": "initial_status",
            "online_friends": online_friends,
            "online_count": len(online_friends),
        }
        await self.send(text_data=json.dumps(payload))

    # Called when a notification is sent to this user's group
    async def notify(self, event):
        await self.send(text_data=json.dumps(event["content"]))