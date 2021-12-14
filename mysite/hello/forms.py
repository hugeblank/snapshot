from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField

from . import models

def must_be_unique(value):
    user_objects = models.FancyUser.objects.filter(email=value)
    if len(user_objects) > 0:
        raise forms.ValidationError("A user with that email already exists")
    # Always return the cleaned data
    return value

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
        model = models.FancyUser
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
        instance.author = models.FancyUser.objects.get(username=request.user.username)
        instance.save()
        return instance

class PostCommentForm(forms.Form):
    comment = forms.CharField()

    def save(self, request, post_id):
        instance = models.PostComment()
        instance.comment = self.cleaned_data['comment']
        instance.author = models.FancyUser.objects.get(username=request.user.username)
        instance.post = models.SnapshotPost.objects.get(id=post_id)
        if (instance.post):
            instance.save()
        return instance


class FollowUserForm(forms.Form):
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
        instance.liker = models.FancyUser.objects.get(username=liker)
        if not models.LikePost.objects.exists(liker=liker, post=post_id):
            instance.save()
        else:
            models.LikePost.objects.delete(post_id=post_id, liker=liker)
        return instance