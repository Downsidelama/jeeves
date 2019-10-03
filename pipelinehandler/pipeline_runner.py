import os
import subprocess
import uuid
from concurrent.futures.thread import ThreadPoolExecutor

from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus
from jeeves import settings
from pipelinehandler.pipeline_command_generator import PipeLineCommandGenerator
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class PipeLineRunner:
    executor = ThreadPoolExecutor(max_workers=3)

    @staticmethod
    def run_pipeline(pipeline: PipeLine, branch="master", revision=""):
        script = PipeLineScriptParser().parse(pipeline.script)
        command_generator = PipeLineCommandGenerator(parsed_script=script, repository=pipeline.repo_url)
        commands = command_generator.get_commands()
        last_results = PipeLineResult.objects.filter(pipeline=pipeline).last()
        version = last_results.version + 1 if last_results else 1

        for subversion, command in enumerate(commands):
            PipeLineRunner.create_entry_and_start_pipeline(command, pipeline, version, subversion)

    @staticmethod
    def create_entry_and_start_pipeline(command, pipeline, version, subversion):
        pipeline_results = PipeLineResult.objects.create()
        pipeline_results.triggered_by = pipeline.user.username
        pipeline_results.version = version
        pipeline_results.subversion = subversion
        pipeline_results.pipeline = pipeline
        pipeline_results.config = pipeline.script
        pipeline_results.command = command
        pipeline_results.status = PipeLineStatus.IN_QUEUE.value
        pipeline_results.save()
        PipeLineRunner.executor.submit(PipeLineRunner.run_docker_process, command, pipeline_results)

    @staticmethod
    def run_docker_process(command, pipeline_results: PipeLineResult):
        pipeline_results.status = PipeLineStatus.IN_PROGRESS.value
        pipeline_results.save()
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
