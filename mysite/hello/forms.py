import re
from hashlib import sha256
from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.db.models.expressions import Random

from . import models

def must_be_unique(value):
    user_objects = models.FancyUser.objects.filter(email=value)
    if len(user_objects) > 0:
        raise forms.ValidationError("A user with that email already exists")
    # Always return the cleaned data
    return value

# TODO does is_valid validate fields that have no custom validators?

class RegistrationForm(UserCreationForm):
# Shamelessly stolen from the examples repo, hopefully forgiven by effort put into other places
    email = forms.EmailField(
        label="Email",
        required=True,
        validators=[must_be_unique]
    )

    image = forms.ImageField(
        label = "Profile Image"
    )

    class Meta:
        model = models.User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "image"
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.image = self.cleaned_data.get('image')
        if commit:
            user.save()
        return user

class PostSnapshotForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=255)
    
    def save(self, request):
        instance = models.SnapshotPost()
        instance.image = self.cleaned_data.get('image')
        instance.caption = self.cleaned_data.get('caption')
        instance.author = request.user
        instance.save()
        return instance

class PostCommentForm(forms.Form):
    comment = forms.CharField()

    def save(self, request):
        post_id = request.GET.get('post_id')
        if (models.SnapshotPost.objects.exists(id=post_id)):
            instance = models.PostComment()
            instance.comment = self.cleaned_data['comment']
            instance.author = request.user
            instance.post = models.SnapshotPost.objects.get(id=post_id)
            if (instance.post):
                instance.save()
            return instance


class FollowUserForm(forms.Form): # TODO: following_user could just be request.user
    def save(self, request, following_user, followed_user):
        instance = models.FollowUser()
        instance.following_user = following_user
        instance.followed_user = followed_user
        if following_user != followed_user:
            if not models.FollowUser.objects.exists(following_user=following_user, followed_user=followed_user):
                instance.save()
            else:
                models.LikePost.objects.delete(following_user=following_user, followed_user=followed_user)
        return instance

class LikePostForm(forms.Form):
    def save(self, request, post_id, liker):
        instance = models.LikePost()
        instance.post = models.SnapshotPost.objects.get(id=post_id)
        instance.liker = request.user
        if not models.LikePost.objects.exists(liker=liker, post=post_id):
            instance.save()
        else:
            models.LikePost.objects.delete(post_id=post_id, liker=liker)
        return instance

class MessageRoomForm(forms.Form): # Create a DM Room, providing a list of usernames
    users = forms.TextInput() # Hopefullly comma separated list of users
    # TODO clean and parse users

    def save(self, users_str):
        room_instance = models.MessageRoom()
        # Generate 64 character room name
        key = sha256()
        key.update(str(room_instance.id).encode())
        key.update("SNAPSHOT_SALT")
        room_instance.key = key.hexdigest()
        users = re.findall(r'[^,\s]+',users_str) # Split string on commas and spaces.
        # Derived from https://stackoverflow.com/questions/44785374/python-re-split-string-by-commas-and-space
        for username in users:
            if (models.User.objects.exists(username=username)):
                room_instance.users.add(models.User.objects.get(username=username))
        room_instance.save()

        return room_instance