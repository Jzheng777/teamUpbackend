# Generated by Django 5.1 on 2024-09-12 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamUpapp', '0011_rename_discordlink_userprofile_discord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='discord',
            field=models.URLField(blank=True, null=True),
        ),
    ]
