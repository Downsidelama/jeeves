import logging
import os
import subprocess
import time
import uuid
from concurrent.futures.thread import ThreadPoolExecutor

from django.utils.timezone import now
from dotenv import load_dotenv
import github3

from dashboard.models import PipeLine, PipeLineResult
from dashboard.pipeline_status import PipeLineStatus
from github_webhook_handler.github_event_status import GithubEventStatus
from jeeves import settings
from pipelinehandler.pipeline_command_generator import PipeLineCommandGenerator
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class PipeLineRunner:
    watchers = ThreadPoolExecutor(max_workers=10)
    executor = ThreadPoolExecutor(max_workers=3)

    def __init__(self, pipeline: PipeLine, branch="master", revision="", installation_id=-1, pull_request_number=-1):
        self.pipeline = pipeline
        self.branch = branch
        self.revision = revision
        self.installation_id = installation_id
        self.pull_request_number = pull_request_number

    def run_pipeline(self):
        try:
            script = PipeLineScriptParser().parse(self.pipeline.script)
            if self.pull_request_number != -1:
                command_generator = PipeLineCommandGenerator(parsed_script=script, repository=self.pipeline.repo_url,
                                                             number=self.pull_request_number)
            else:
                command_generator = PipeLineCommandGenerator(parsed_script=script, repository=self.pipeline.repo_url,
                                                             branch=self.branch, revision=self.revision)
            commands = command_generator.get_commands()
            last_results = PipeLineResult.objects.filter(pipeline=self.pipeline).last()
            version = last_results.version + 1 if last_results else 1

            pipeline_results = []
            futures = []
            for subversion, command in enumerate(commands):
                pipeline_result, future = self.create_entry_and_start_pipeline(command, self.pipeline, version,
                                                                               subversion)
                pipeline_results.append(pipeline_result)
                futures.append(future)

            if self.pipeline.is_github_pipeline:
                self.watchers.submit(self.start_watcher, pipeline_results, futures)
        except ValueError as e:
            if self.pipeline.is_github_pipeline:
                self.set_ci_status(status=GithubEventStatus.FAILURE, description=str(e))

    def create_entry_and_start_pipeline(self, command, pipeline, version, subversion):
        pipeline_result = PipeLineResult.objects.create(installation_id=self.installation_id,
                                                        pull_request_number=self.pull_request_number,
                                                        revision=self.revision, branch=self.branch,
                                                        type="Pull Request" if self.pull_request_number != -1 else 'Push')
        pipeline_result.triggered_by = pipeline.user.username
        pipeline_result.version = version
        pipeline_result.subversion = subversion
        pipeline_result.pipeline = pipeline
        pipeline_result.config = pipeline.script
        pipeline_result.command = command
        pipeline_result.status = PipeLineStatus.IN_QUEUE.value
        pipeline_result.save()
        future = self.executor.submit(self.run_docker_process, command, pipeline_result)
        return pipeline_result, future

    @staticmethod
    def run_docker_process(command, pipeline_result: PipeLineResult):
        pipeline_result.build_start_time = now()
        pipeline_result.status = PipeLineStatus.IN_PROGRESS.value
        pipeline_result.save()
        output_file_path = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(output_file_path, exist_ok=True)
        output_file_name = "{}.log".format(uuid.uuid4())

        with open(os.path.join(output_file_path, output_file_name), 'wb+') as output:
            with subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=output) as process:

                process.wait()
                return_code = process.returncode

            if return_code == 0:
                pipeline_result.status = PipeLineStatus.SUCCESS.value
            else:
                pipeline_result.status = PipeLineStatus.FAILED.value
            pipeline_result.build_end_time = now()
            pipeline_result.save()

        with open(os.path.join(output_file_path, output_file_name), 'r', encoding='utf8') as output:
            pipeline_result.log = str(output.read())
            pipeline_result.save()

    def start_watcher(self, pipeline_results, futures):
        """Starts a watcher for all current pipeline running.
            GitHub pipelines only!
            If any of them fails, then it sets the commit/PR status to failed.
            It sets it to success otherwise.
        """
        while not all(
                pipeline_result.status in [PipeLineStatus.FAILED.value, PipeLineStatus.SUCCESS.value] for
                pipeline_result in pipeline_results):
            time.sleep(1)

        for future in futures:
            if future.exception():
                try:
                    raise future.exception()
                except Exception as e:
                    logging.exception('Exception during pipeline.')

        context = "Jeeves CI - {}".format(pipeline_results[0].type)
        if any(pipeline_result.status == PipeLineStatus.FAILED.value for
               pipeline_result in pipeline_results):
            logging.debug("setting pipeline to failed")
            self.set_ci_status(context=context, status=GithubEventStatus.FAILURE, description="PipeLine failed.")
        else:
            logging.debug("setting pipeline to success")
            self.set_ci_status(context=context, status=GithubEventStatus.SUCCESS, description="PipeLine successful.")

    def set_ci_status(self, commit: str = None, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        logging.debug("Setting CI status to {}".format(status.value))
        if not commit:
            commit = self.revision
        client = self.get_github_client()
        repository = self.get_repository(client)
        print(repository.create_status(commit, status.value, context=context, description=description))

    def get_repository(self, github_client):
        try:
            return github_client.repository(self.pipeline.user.username, self.pipeline.name)
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)

    def get_github_client(self):
        load_dotenv()
        GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
        GITHUB_APP_IDENTIFIER = os.getenv('GITHUB_APP_IDENTIFIER')

        client = github3.GitHub()
        client.login_as_app_installation(GITHUB_PRIVATE_KEY.encode(), GITHUB_APP_IDENTIFIER, self.installation_id)
        return client
