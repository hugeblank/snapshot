from django.db import models
from django.contrib.auth.models import User
import hashlib
import datetime
import os

# Create your models here.


class UserInfo(models.Model):
    def path(instance, filename):
        return 'images/' + instance.username + '/profile' + os.path.splitext(filename)

    image = models.ImageField(upload_to=path)
    user = models.OneToOneField(User)
    # timestamp can be found in the date_joined field.


class SnapshotPost(models.Model):
    def path(instance, filename):
        # Assign each file a unique hash per-user
        sha = hashlib.sha256()
        time = datetime.datetime.now().isoformat()
        file = instance.image.file.open()
        for line in file:
            sha.update(line)
        sha.update(time.encode())
        # swap out the file name with a (hopefully unique) hash
        return 'images/' + instance.author.username + '/' + sha.hexdigest() + os.path.splitext(filename)

    image = models.ImageField(upload_to=path)
    caption = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class PostComment(models.Model):
    post = models.ForeignKey(SnapshotPost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class LikePost(models.Model):
    post = models.ForeignKey(SnapshotPost, on_delete=models.CASCADE)
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class FollowUser(models.Model):
    following_user = models.ForeignKey(
        User, related_name="following_user", on_delete=models.CASCADE)
    followed_user = models.ForeignKey(
        User, related_name="followed_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class MessageRoom(models.Model):
    key = models.CharField(max_length=64)  # unique hash for rooms (sha256)
    users = models.ManyToManyField(User, on_delete=models.DO_NOTHING)

class Message(models.Model):
    message = models.TextField(max_length=1024)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="sender")
    room = models.ForeignKey(MessageRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
