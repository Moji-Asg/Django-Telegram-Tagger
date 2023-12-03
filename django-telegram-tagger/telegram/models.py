from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


# Create your models here.
class SettingsModel(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False, unique=True)
    value = models.TextField(null=False, blank=False)
    date_modified = models.DateTimeField(auto_now=True)


class ChatsModel(models.Model):
    chat_id = models.BigIntegerField(db_index=True, unique=True)
    title = models.CharField(max_length=128, null=False, blank=False)
    username = models.CharField(max_length=32, validators=[MinLengthValidator(5)], null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    invite_link = models.CharField(max_length=128, null=True, blank=True)


class UsersModel(models.Model):
    user_id = models.BigIntegerField(db_index=True, unique=True)
    first_name = models.CharField(max_length=64, null=False, blank=False)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    username = models.CharField(max_length=32, validators=[MinLengthValidator(5)], null=True, blank=True)


class CustomUserModel(AbstractUser):
    user = models.ForeignKey(UsersModel, models.CASCADE)
    first_name = None
    last_name = None

    REQUIRED_FIELDS = []
