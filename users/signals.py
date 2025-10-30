# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from .models import Profile

# When a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# When a user logs in — make sure profile exists
@receiver(user_logged_in, sender=User)
def ensure_user_profile_exists(sender, user, request, **kwargs):
    Profile.objects.get_or_create(user=user)
