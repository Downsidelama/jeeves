import subprocess

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from dashboard.models import PipeLine
from pipelinehandler.pipeline_command_generator import PipeLineCommandGenerator
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class GithubPipeLineHandlerView(View):
    def get(self, request):
        return HttpResponse("OK")


class DashboardPipeLineHandlerView(View):
    # TODO: Threading
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        script = PipeLineScriptParser().parse(pipeline.script)
        command_generator = PipeLineCommandGenerator(parsed_script=script, repository=pipeline.repo_url)

        command = command_generator.get_command()
        print(command)
        with subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE) as process:
            for line in process.stdout:
                print(line.decode(), end='')

            process.wait()


        return HttpResponse(command)
