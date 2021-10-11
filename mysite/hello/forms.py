from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as auth_user

from . import models

def must_be_unique(value):
    user_objects = auth_user.objects.filter(email=value)
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

    class Meta:
        model = auth_user
        fields = (
            "username",
            "email",
            "password1",
            "password2"
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class PostSnapshotForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=255)
    
    def save(self, request):
        instance = models.SnapshotPostModel()
        instance.image = self.cleaned_data.get('image')
        instance.caption = self.cleaned_data.get('caption')
        instance.author = request.author.username
        instance.save()
        return instance

class PostCommentForm(forms.Form):
    comment = forms.CharField()

    def save(self, request, post_id):
        instance = models.PostCommentModel()
        instance.comment = self.cleaned_data['comment']
        instance.author = request.user
        instance.post = models.SnapshotPostModel.objects.get(id=post_id)
        instance.save()
        return instance
