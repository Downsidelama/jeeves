import logging

import urllib3

from github_webhook_handler.github_event_status import GithubEventStatus
from . import GitHubEventHandler


class PushEventHandler(GitHubEventHandler):
    config_file_url = 'https://raw.githubusercontent.com/{user}/{repo_name}/{revision}/.jeeves.yml'
    url_loader = urllib3.PoolManager()

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def get_repository(self):
        try:
            return self.github_client.repository(self.payload['repository']['owner']['login'],
                                                 self.payload['repository']['name'])
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)

    def _handle_event(self):
        self._make_installation_client()
        if self.github_client:
            self.repository = self.get_repository()
        else:
            self._set_response('ERROR', "Couldn't handle event")
            return

        try:
            config_file_content = self._get_config_file_content()
        except (KeyError, ValueError):
            logging.exception("Couldn't handle event", exc_info=True)
            self._set_response('ERROR', "Couldn't handle event")
            return

        # PipeLineRunner.run_pipeline(None, revision='')

        self.set_ci_status(status=GithubEventStatus.SUCCESS)
        self._set_response('OK', "In progress")

    def _get_config_file_content(self):
        try:
            revision = self.payload['after']
            user = self.payload['repository']['owner']['login']
            repo_name = self.payload['repository']['name']

            current_config = self.config_file_url.format(user=user, repo_name=repo_name, revision=revision)
            response: urllib3.HTTPResponse = self.url_loader.request('GET', current_config)

            if response.status == 200:
                yaml = response.read()  # TODO: Make it safe (don't allow huge amounts of data)
            else:
                raise ValueError("Yaml file doesn't exists in the repository at this revision")

            return yaml
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)
            return ''

    def set_ci_status(self, commit: str = None, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        try:
            if commit is None:
                commit = self.payload['after']
            self.repository.create_status(commit, status.value, context=context, description=description)
        except KeyError:
            self._set_response('ERROR', "Invalid payload")
            logging.exception("Invalid payload", exc_info=True)
