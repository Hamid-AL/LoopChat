from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

# Direct Message
class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

# Chat Room
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(User, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='joined_rooms')

    def __str__(self):
        return self.name

# Room Message
class RoomMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)