# Generated by Django 5.1 on 2024-09-04 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamUpapp', '0005_userprofile_exp'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_protected',
            field=models.BooleanField(default=False),
        ),
    ]
