import subprocess
import threading
import uuid

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from dashboard.models import PipeLine, PipeLineOutput
from pipelinehandler.pipeline_command_generator import PipeLineCommandGenerator
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class GithubPipeLineHandlerView(View):
    def get(self, request):
        return HttpResponse("OK")


class DashboardPipeLineHandlerView(View):
    # TODO: Threading
    def get(self, request, pk):
        pipeline = get_object_or_404(PipeLine, pk=pk)
        pipeline_output = PipeLineOutput()
        pipeline_output.pipeline = pipeline
        script = PipeLineScriptParser().parse(pipeline.script)
        command_generator = PipeLineCommandGenerator(parsed_script=script, repository=pipeline.repo_url)

        command = command_generator.get_command()
        docker_thread = threading.Thread(target=self.run_docker_process, args=(command, pipeline_output,))
        docker_thread.start()

        return HttpResponse(command)

    def run_docker_process(self, command, pipeline_output: PipeLineOutput):
        pipeline_output.results = 'in_progress'
        with open('C:\\docker_logs\\{}.log'.format(uuid.uuid4()), 'w+') as output:  # TODO: make it platform independent
            with subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE) as process:
                for line in process.stdout:
                    print(line, end='')
                pipeline_output.results = 'success' if process.wait() == 0 else 'error'

            pipeline_output.log = output.read()
        pipeline_output.save()
