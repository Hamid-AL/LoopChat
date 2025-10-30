

# users/models.py
from django.db import models
from django.contrib.auth.models import User

class Friendship(models.Model):
    from_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='friendships_sent')
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='friendships_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_profile', 'to_profile')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    friends = models.ManyToManyField(
        'self',
        through='Friendship',
        through_fields=('from_profile', 'to_profile'),
        symmetrical=True,
        blank=True
    )
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Profile of {self.user.username}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="received_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    class Meta:
        unique_together = ['from_user', 'to_user']

    def accept(self):
        """Accept friend request and create friendship"""
        self.status = 'accepted'
        self.save()
        self.from_user.friends.add(self.to_user)
        # symmetrical=True automatically adds reverse relationship

    def reject(self):
        """Reject friend request"""
        self.status = 'rejected'
        self.save()
