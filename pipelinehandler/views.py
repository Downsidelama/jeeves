from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from dashboard.models import PipeLine
from pipelinehandler.pipeline_runner import PipeLineRunner


class GithubPipeLineHandlerView(View):
    def get(self, request):
        return HttpResponse("OK")


class DashboardPipeLineHandlerView(View):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        PipeLineRunner.run_pipeline(pipeline)
        return redirect(pipeline)
