from django.db import models
from django.urls import reverse

from jeeves import settings

User = settings.AUTH_USER_MODEL


class PipeLine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    script = models.TextField(default="", blank=True)
    repo_url = models.URLField(default="")

    def get_absolute_url(self):
        return reverse('dashboard:view_pipeline', kwargs={'pk': self.pk})


class PipeLineOutput(models.Model):
    pipeline = models.ForeignKey(PipeLine, on_delete=models.CASCADE)
    log = models.TextField()
    results = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
