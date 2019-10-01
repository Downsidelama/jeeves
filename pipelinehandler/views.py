import os
import subprocess
import threading
import uuid

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus
from jeeves import settings
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
        commands = command_generator.get_commands()
        last_results = PipeLineResult.objects.filter(pipeline=pipeline).last()
        version = last_results.version + 1 if last_results else 1

        for subversion, command in enumerate(commands):
            self.create_entry_and_start_pipeline(command, pipeline, version, subversion)

        return redirect(pipeline)

    def create_entry_and_start_pipeline(self, command, pipeline, version, subversion):
        pipeline_results = PipeLineResult.objects.create()
        pipeline_results.triggered_by = pipeline.user.username
        pipeline_results.version = version
        pipeline_results.subversion = subversion
        pipeline_results.pipeline = pipeline
        pipeline_results.config = pipeline.script
        pipeline_results.command = command
        pipeline_results.status = PipeLineStatus.IN_PROGRESS.value
        pipeline_results.save()
        docker_thread = threading.Thread(target=self.run_docker_process, args=(command, pipeline_results))
        docker_thread.start()

    def run_docker_process(self, command, pipeline_results: PipeLineResult):
        output_file_path = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(output_file_path, exist_ok=True)
        output_file_name = "{}.log".format(uuid.uuid4())

        with open(os.path.join(output_file_path, output_file_name), 'w+') as output:
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
