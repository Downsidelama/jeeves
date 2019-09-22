from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    social_uid = models.TextField(null=True, blank=True)


def get_social_uid(backend, user, response, *args, **kwargs):
    user.social_uid = kwargs['uid']
    user.save()
