from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    search_history = models.JSONField(default=list)
    make_private = models.BooleanField(default=False)
    allow_follow = models.BooleanField(default=True)
    show_ranking = models.BooleanField(default=True)
    profanity_filter = models.BooleanField(default=True)
    picture = models.URLField(blank=True, default='')

    def __str__(self):
        return self.user.username



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    thumbnail_url = models.URLField(blank=True)
    type = models.CharField(max_length
    =20, default='post')
    attributes = models.JSONField(default=dict)
    recipient_group = models.ForeignKey('Group', null=True, blank=True, on_delete=models.SET_NULL)

class Connection(models.Model):
    to_user = models.ForeignKey(User, related_name='connections_to', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='connections_from', on_delete=models.CASCADE)
    attributes = models.JSONField(default=dict)

class Group(models.Model):
    name = models.CharField(max_length=100)

class GroupMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class PostReaction(models.Model):
    reactor = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

