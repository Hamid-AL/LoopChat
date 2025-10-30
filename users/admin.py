from django.contrib import admin
from .models import Profile, Friendship, FriendRequest
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at')
    search_fields = ('user__username', 'bio')
    list_filter = ('created_at',)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_profile', 'to_profile', 'created_at')
    search_fields = ('from_profile__user__username', 'to_profile__user__username')
    list_filter = ('created_at',)

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'status')
    search_fields = ('from_user__user__username', 'to_user__user__username')
    list_filter = ('created_at', 'status')




