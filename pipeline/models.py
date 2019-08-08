from django.db import models
from django.contrib.auth.models import User


class PipeLine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()


class PipeLineItemType(models.Model):
    name = models.CharField(max_length=255)


class PipeLineItem(models.Model):
    pipeline = models.ForeignKey(PipeLine, on_delete=models.CASCADE)
    type = models.ForeignKey(PipeLineItemType, on_delete=models.CASCADE)
