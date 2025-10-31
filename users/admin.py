from django.contrib import admin
from .models import Profile, Friendship, FriendRequest
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'friends_count', 'friends_list', 'created_at')
    search_fields = ('user__username', 'bio')
    list_filter = ('created_at',)
    
    def friends_count(self, obj):
        return obj.friends.count()
    friends_count.short_description = 'Friends Count'
    
    def friends_list(self, obj):
        friends = obj.friends.all()[:5]  # Limit to 5 for display
        return ", ".join([friend.user.username for friend in friends])
    friends_list.short_description = 'Friends (first 5)'


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




