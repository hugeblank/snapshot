from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.SnapshotPost)
admin.site.register(models.PostComment)
admin.site.register(models.LikePost)
admin.site.register(models.FancyUser)
admin.site.register(models.FollowUser)