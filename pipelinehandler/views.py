import json
import logging

from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import PipeLine
from pipelinehandler.pipeline_runner import PipeLineRunner


class GithubPipeLineHandlerView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest):
        try:
            request_body = json.loads(request.body)
            pipeline = get_object_or_404(PipeLine, pk=request_body['pipeline_id'])
            pipeline.repo_url = request_body['html_url']
            pipeline.script = request_body['config_file_content']
            if 'number' in request_body:
                PipeLineRunner(pipeline, revision=request_body['commit_sha'],
                               installation_id=request_body['installation_id'],
                               pull_request_number=request_body['number']).run_pipeline()
            else:
                branch = request_body['ref'].split('/')[-1]
                PipeLineRunner(pipeline, revision=request_body['commit_sha'],
                               installation_id=request_body['installation_id'], branch=branch).run_pipeline()
            return HttpResponse("OK")
        except:
            logging.exception("Error during pipeline setup.")
            return HttpResponse("Error")



class DashboardPipeLineHandlerView(View):
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        PipeLineRunner(pipeline).run_pipeline()
        return redirect(pipeline)
