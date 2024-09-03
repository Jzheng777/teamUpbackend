# Generated by Django 5.1 on 2024-08-28 19:18

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamUpapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Reaction',
            new_name='PostReaction',
        ),
        migrations.RemoveField(
            model_name='fileupload',
            name='user',
        ),
        migrations.AddField(
            model_name='fileupload',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='connection',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_from', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='connection',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teamUpapp.post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='recipient_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teamUpapp.group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='type',
            field=models.CharField(default='post', max_length=20),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_history', models.JSONField(default=list)),
                ('make_private', models.BooleanField(default=False)),
                ('allow_follow', models.BooleanField(default=True)),
                ('show_ranking', models.BooleanField(default=True)),
                ('picture', models.URLField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
