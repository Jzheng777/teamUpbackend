from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name == 'teamUpapp':
        group_data = [
            {'name': 'FPS', 'is_protected': True},
            {'name': 'Battle-Royale', 'is_protected': True},
            {'name': 'MOBA', 'is_protected': True},
            {'name': 'Sandbox', 'is_protected': True},
            {'name': 'Action-Adventure', 'is_protected': True},
        ]

        for group_info in group_data:
            Group.objects.update_or_create(name=group_info['name'], defaults={'is_protected': group_info['is_protected']})


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    search_history = models.JSONField(default=list)
    make_private = models.BooleanField(default=False)
    allow_follow = models.BooleanField(default=True)
    show_ranking = models.BooleanField(default=True)
    profanity_filter = models.BooleanField(default=True)
    picture = models.URLField(blank=True, default='')
    exp = models.IntegerField(default=0)
    find = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    discord = models.TextField(blank=True, null=True)
    ranks = models.JSONField(default=dict)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    attributes = models.JSONField(default=dict)
    recipient_group = models.ForeignKey('Group', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class Connection(models.Model):
    to_user = models.ForeignKey(User, related_name='connections_to', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='connections_from', on_delete=models.CASCADE)
    attributes = models.JSONField(default=dict)


class Group(models.Model):
    name = models.CharField(max_length=100)
    is_protected = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.is_protected:
            raise Exception(f'The group "{self.name}" cannot be deleted because it is protected.')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

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
