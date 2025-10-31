from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from .models import FriendRequest, Profile
from chat.models import ChatRoom
# -------- LOGIN --------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("chat:friends") #redirect("chat:index")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("users:login")

    return render(request, "users/login.html")


# -------- SIGNUP --------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("users:signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("users:signup")

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("users:login")

    return render(request, "users/signup.html")
# -------- LOGOUT --------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("users:login")


# -------- SEND FRIEND REQUEST --------
@login_required(login_url='users:login')
def send_friend_request(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect(request.META.get('HTTP_REFERER', 'users:home'))

    to_user = get_object_or_404(Profile, user__id=user_id)
    from_profile = request.user.profile

    # Check if a request already exists in either direction and if it's accepted
    existing_request_forward = FriendRequest.objects.filter(
        from_user=from_profile, to_user=to_user
    ).first()
    
    existing_request_reverse = FriendRequest.objects.filter(
        from_user=to_user, to_user=from_profile
    ).first()
    
    existing_request = existing_request_forward or existing_request_reverse

    if existing_request and existing_request.status == 'accepted':
        messages.error(request, f"You are already friends with {to_user.user.username}.")
    else:
        # Delete existing pending/rejected request if it exists before creating a new one
        if existing_request:
            existing_request.delete()
        FriendRequest.objects.create(from_user=from_profile, to_user=to_user)
        messages.success(request, f"Friend request sent to {to_user.user.username} successfully.")

    return redirect(request.META.get('HTTP_REFERER', 'users:home'))


# -------- ACCEPT FRIEND REQUEST --------
@login_required(login_url='users:login')
def accept_friend_request(request, request_id):
    f_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user.profile
    )

    if f_request.status != 'pending':
        messages.error(request, "This friend request has already been handled.")
        return redirect(request.META.get('HTTP_REFERER', 'users:home'))

    # Accept the request and create friendship
    f_request.accept()
    messages.success(request, f"You are now friends with {f_request.from_user.user.username}.")

    return redirect(request.META.get('HTTP_REFERER', 'users:home'))

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user.profile)
    friend_request.reject()
    messages.info(request, 'Friend request rejected.')
    return redirect('chat:friends')

@login_required
def remove_friend(request, user_id):
    friend_user = get_object_or_404(User, id=user_id)
    friend_profile = friend_user.profile

    # i need to delete friend request
    # you need to delete from each side(but only one exists at a time)
    try:
        FriendRequest.objects.filter(from_user=request.user.profile, to_user=friend_profile).delete()
        FriendRequest.objects.filter(from_user=friend_profile, to_user=request.user.profile).delete()
    except FriendRequest.DoesNotExist:
        pass
    # Remove from both sides (due to symmetrical relationship)
    request.user.profile.friends.remove(friend_profile)
    messages.success(request, f'Removed {friend_user.username} from friends.')
    
    return redirect('chat:friends')


