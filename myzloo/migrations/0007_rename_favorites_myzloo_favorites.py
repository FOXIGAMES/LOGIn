# Generated by Django 4.2.3 on 2023-07-25 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myzloo', '0006_favorites'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Favorites',
            new_name='myzloo_favorites',
        ),
    ]
