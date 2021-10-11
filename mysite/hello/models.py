from django.db import models
from django.contrib.auth.models import User as auth_user
import hashlib

# Create your models here.
class SnapshotPostModel(models.Model):
    caption = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(auth_user, on_delete=models.CASCADE)
    
    def path(instance, filename):
        # Assign each file a unique hash per-user
        sha = hashlib.sha256()
        file = instance.image.file.open()
        for line in file:
            sha.update(line)
            print(line)
        # swap out the file name with a (hopefully unique) hash
        return 'images/' + instance.author.username + '/' + sha.hexdigest()

    image = models.ImageField(upload_to=path)

class PostCommentModel(models.Model):
    comment = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(auth_user, on_delete=models.CASCADE)
    post = models.ForeignKey(SnapshotPostModel, on_delete = models.CASCADE)
