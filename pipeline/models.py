from django.db import models
from django.contrib.auth.models import User


class PipeLine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    script = models.TextField()
    repo_url = models.TextField()
