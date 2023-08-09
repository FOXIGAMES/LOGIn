# Generated by Django 4.2.3 on 2023-07-28 08:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myzloo', '0015_alter_customuser_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='favorite_tracks',
            field=models.ManyToManyField(related_name='favorited_by_users', through='myzloo.myzloo_favorites', to='myzloo.musictrack'),
        ),
        migrations.AlterField(
            model_name='myzloo_favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites_tracks', to=settings.AUTH_USER_MODEL),
        ),
    ]
