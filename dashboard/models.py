from django.db import models
from django.urls import reverse

from dashboard.pipeline_status import PipeLineStatus
from jeeves import settings

User = settings.AUTH_USER_MODEL


class PipeLine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    script = models.TextField(default="", blank=True)
    repo_url = models.URLField(default="")
    is_github_pipeline = models.BooleanField(default=False)
    site_private = models.BooleanField(default=False)  # Should we display it on the website?

    #  Github pipeline stuff
    is_active = models.BooleanField(default=True)
    repository_id = models.IntegerField(null=True, default=None, unique=True)
    commit_sha = models.CharField(max_length=40, null=True, default=None)

    def get_absolute_url(self):
        return reverse('dashboard:view_pipeline', kwargs={'pk': self.pk})


class PipeLineResult(models.Model):
    pipeline = models.ForeignKey(PipeLine, on_delete=models.CASCADE, default=1)
    triggered_by = models.TextField(default="")
    version = models.IntegerField(default=1)
    subversion = models.IntegerField(default=1)
    command = models.TextField(default="")
    status = models.IntegerField(default=PipeLineStatus.IN_PROGRESS.value)
    log = models.TextField(default="")
    config = models.TextField(default="")
    # TODO: BUILD START TIME!
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
