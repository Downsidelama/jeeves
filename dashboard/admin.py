from django.contrib import admin

from .models import PipeLine, PipeLineOutput

admin.site.register(PipeLine)
admin.site.register(PipeLineOutput)
