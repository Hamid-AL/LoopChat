from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_room, name="create_room"),
    path("delete/<str:room_name>/", views.delete_room, name="delete_room"),
    path("room/<str:room_name>/", views.room_chat, name="room_chat"),  # your existing room view,
    path("user/<str:recipient_name>/", views.private_chat, name="private_chat"),
    path("friends/", views.friends, name="friends"),
]   