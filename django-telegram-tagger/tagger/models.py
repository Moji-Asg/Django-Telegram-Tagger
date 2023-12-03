from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UsersMessagesModel(models.Model):
    user = models.ForeignKey('telegram.UsersModel', models.CASCADE)
    chat = models.ForeignKey('telegram.ChatsModel', models.CASCADE)
    message_id = models.BigIntegerField()
    date_modified = models.DateTimeField(auto_now=True)
