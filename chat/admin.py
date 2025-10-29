
from django.contrib import admin
from .models import DirectMessage, ChatRoom, RoomMessage

#admin.site.register(DirectMessage)
#admin.site.register(ChatRoom)
#admin.site.register(RoomMessage)

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')
    search_fields = ('name',)

@admin.register(RoomMessage)
class RoomMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'timestamp')
    list_filter = ('room', 'timestamp')

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read')
    list_filter = ('is_read',)
