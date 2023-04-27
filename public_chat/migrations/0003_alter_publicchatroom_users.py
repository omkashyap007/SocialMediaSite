# Generated by Django 3.2 on 2022-09-30 09:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('public_chat', '0002_rename_time_stamp_publicroomchatmessage_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicchatroom',
            name='users',
            field=models.ManyToManyField(blank=True, help_text='Users who are connected to the chat room !', to=settings.AUTH_USER_MODEL),
        ),
    ]
