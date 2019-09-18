import os
import subprocess
import threading
import uuid

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus
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
        pipeline_results = PipeLineResult.objects.create()
        pipeline_results.pipeline = pipeline
        pipeline_results.config = pipeline.script
        pipeline_results.status = PipeLineStatus.IN_PROGRESS.value
        pipeline_results.save()

        command = command_generator.get_command()
        docker_thread = threading.Thread(target=self.run_docker_process, args=(command, pipeline_results))
        docker_thread.start()

        return redirect(pipeline)

    def run_docker_process(self, command, pipeline_results: PipeLineResult):
        output_file_path = "C:\\docker_logs\\"
        output_file_name = "{}.log".format(uuid.uuid4())

        with open(os.path.join(output_file_path, output_file_name), 'w+') as output:  # TODO: make it platform independent
            with subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=output) as process:

                process.wait()
                return_code = process.returncode

            if return_code == 0:
                pipeline_results.status = PipeLineStatus.SUCCESS.value
            else:
                pipeline_results.status = PipeLineStatus.FAILED.value

        with open(os.path.join(output_file_path, output_file_name), 'r', encoding='utf8') as output:
            pipeline_results.log = str(output.read())
            pipeline_results.save()
