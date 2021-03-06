from django.db import models
from django.urls import reverse
from picklefield.fields import PickledObjectField

from dashboard.pipeline_status import PipeLineStatus
from jeeves import settings

User = settings.AUTH_USER_MODEL


class PipeLine(models.Model):
    """Model used to represent the PipeLine data."""
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

    def get_absolute_url(self):
        return reverse('dashboard:view_pipeline', kwargs={'pk': self.pk})


class PipeLineResult(models.Model):
    """Model used to represent the PipeLineResult data."""
    pipeline = models.ForeignKey(PipeLine, on_delete=models.CASCADE, default=1)
    triggered_by = models.TextField(default="")
    version = models.IntegerField(default=1)
    subversion = models.IntegerField(default=1)
    command = PickledObjectField(null=True)
    language = models.TextField()
    status = models.IntegerField(default=PipeLineStatus.IN_PROGRESS.value)
    log = models.TextField(default="")
    config = models.TextField(default="")
    type = models.TextField(default="push")  # push / pull_request
    revision = models.TextField()
    branch = models.TextField()
    installation_id = models.IntegerField()
    pull_request_number = models.IntegerField(default=-1)
    build_start_time = models.DateTimeField(null=True, default=None)
    build_end_time = models.DateTimeField(null=True, default=None)
    log_file_name = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
