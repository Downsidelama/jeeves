import os
import urllib3

from django.http import HttpRequest

from github_webhook_handler.github_event_status import GithubEventStatus
from pipelinehandler.pipeline_runner import PipeLineRunner
from . import GitHubEventHandler


class PushEventHandler(GitHubEventHandler):
    config_file_url = 'https://raw.githubusercontent.com/{user}/{repo_name}/{revision}/.jeeves.yml'
    url_loader = urllib3.PoolManager()

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)
        self._make_installation_client()
        self.repository = self.github_client.repository(payload['repository']['owner']['login'],
                                                        payload['repository']['name'])

    def _handle_event(self):
        config_file_content = self._get_config_file_content()
        # PipeLineRunner.run_pipeline(None, revision='')

        self.set_ci_status(status=GithubEventStatus.SUCCESS)

        self.response['status'] = 'OK'
        self.response['message'] = 'In progress'

    def _get_config_file_content(self):
        revision = self.payload['after']
        user = self.payload['repository']['owner']['login']
        repo_name = self.payload['repository']['name']

        current_config = self.config_file_url.format(user=user, repo_name=repo_name, revision=revision)
        response: urllib3.HTTPResponse = self.url_loader.request('GET', current_config)

        yaml = ''
        if response.status == 200:
            yaml = response.read()  # TODO: Make it safe (don't allow huge amounts of data)
        else:
            raise ValueError("Yaml file doesn't exists in the repository at this revision")

        return yaml

    def set_ci_status(self, commit: str = None, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        if commit is None:
            commit = self.payload['after']
        self.repository.create_status(commit, status.value, context=context, description=description)