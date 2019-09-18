from django.contrib import admin

from .models import PipeLine, PipeLineResult

admin.site.register(PipeLine)
admin.site.register(PipeLineResult)

