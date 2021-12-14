from django.db import models
from django.contrib.auth.models import User
import hashlib
import datetime
import os

# Create your models here.

class FancyUser(User):
    def path(instance, filename):
        return 'images/' + instance.username + '/profile' + os.path.splitext(filename)

    image = models.ImageField(upload_to=path)
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
    author = models.ForeignKey(FancyUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
class PostComment(models.Model):
    post = models.ForeignKey(SnapshotPost, on_delete = models.CASCADE)
    comment = models.CharField(max_length=255)
    author = models.ForeignKey(FancyUser, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
class LikePost(models.Model):
    post = models.ForeignKey(SnapshotPost, on_delete = models.CASCADE)
    liker = models.ForeignKey(FancyUser, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
class FollowUser(models.Model):
    following_user = models.ForeignKey(FancyUser, related_name="following_user", on_delete = models.CASCADE)
    followed_user = models.ForeignKey(FancyUser, related_name="followed_user", on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)