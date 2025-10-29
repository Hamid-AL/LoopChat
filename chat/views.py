


# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, RoomMessage, DirectMessage
import json
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def index(request):
    rooms = ChatRoom.objects.all()  # show all existing rooms
    users= User.objects.all()
    return render(request, "chat/index.html", {"rooms": rooms, "users": users})

@login_required
def create_room(request):
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        if room_name and not ChatRoom.objects.filter(name=room_name).exists():
            room = ChatRoom.objects.create(name=room_name, creator=request.user)
            room.members.add(request.user)
    # redirect to the same page where the user is
    return redirect(request.META.get('HTTP_REFERER', 'chat:index'))

@login_required
def delete_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    room.delete()
    # redirect to the same page where the user is
    return redirect(request.META.get('HTTP_REFERER', 'chat:index'))


@login_required(login_url='users:login')
def room_chat(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    messages = RoomMessage.objects.filter(room=room).order_by("timestamp")

    # Prepare messages for JavaScript
    message_data = [
        {
            "username": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        }
        for msg in messages
    ]

    context = {
        "room_name": room_name,
        "rooms": ChatRoom.objects.all(),
        "messages_json": mark_safe(json.dumps(message_data)),
        "username": request.user.username,
        "users": User.objects.all()
    }

    return render(request, "chat/room_chat.html", context)

# -------- USER --------
@login_required(login_url='users:login')
def private_chat(request, recipient_name):
    private_room_name=f"private_{request.user.username}_{recipient_name}"
    recipient = User.objects.get(username=recipient_name)
    messages = DirectMessage.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by("timestamp")
    print(private_room_name)
    message_data = [
        {
            "sender": msg.sender.username,
            "recipient": msg.recipient.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        } for msg in messages
    ]

   
    context = {
        "room_name": private_room_name,
        "rooms": ChatRoom.objects.all(),
        "messages_json": mark_safe(json.dumps(message_data)),
        "username": request.user.username,
        "recipient_name": recipient_name,
        "users": User.objects.all(),
    }
    return render (request, "chat/user_chat.html", context)