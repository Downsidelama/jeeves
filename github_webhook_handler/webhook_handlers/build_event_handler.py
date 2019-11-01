import json
import logging
from abc import ABC

import urllib3

from github_webhook_handler.github_event_status import GithubEventStatus
from github_webhook_handler.webhook_handlers import GitHubEventHandler


class BuildEventHandler(GitHubEventHandler, ABC):
    """Abstract class to be used as a super class for events which involve running a pipeline"""
    workers = [  # Default worker, can be overwritten with workers.json file
        {
            "id": 1,
            "url": "http://localhost:8000/pipelinehandler/github-pipeline/"
        }
    ]
    config_file_url = 'https://raw.githubusercontent.com/{user}/{repo_name}/{revision}/.jeeves.yml'
    url_loader = urllib3.PoolManager()

    def __init__(self, payload, response):
        super().__init__(payload, response)
        self.repository = self.get_repository()

    def _setup(self):
        self._load_workers()
        self._make_installation_client()

        if self.github_client:
            self.repository = self.get_repository()
        else:
            self._set_response('ERROR', "Couldn't handle event")
            return
        self.set_ci_status(status=GithubEventStatus.PENDING)
        self._handle_event()

    def set_ci_status(self, commit: str = None, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        try:
            if commit is None:
                commit = self.payload['after']
            self.repository.create_status(commit, status.value, context=context, description=description)
        except KeyError:
            self._set_response('ERROR', "Invalid payload")
            logging.exception("Invalid payload", exc_info=True)

    def get_repository(self):
        try:
            return self.github_client.repository(self.payload['repository']['owner']['login'],
                                                 self.payload['repository']['name'])
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)

    def get_free_worker(self):
        return self.workers[0]  # TODO: get the on with the least load on them.

    def _get_config_file_content(self):
        try:
            revision = self.payload['after']
            user = self.payload['repository']['owner']['login']
            repo_name = self.payload['repository']['name']

            current_config = self.config_file_url.format(user=user, repo_name=repo_name, revision=revision)
            response: urllib3.HTTPResponse = self.url_loader.request('GET', current_config)

            if response.status == 200:
                yaml = response.data.decode()  # TODO: Make it safe (don't allow huge amounts of data)
            else:
                raise ValueError("Yaml file doesn't exists in the repository at this revision")
            return yaml
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)
            return ''

    def _load_workers(self):
        try:
            with open('workers.json', 'r') as f:
                self.workers = json.load(f)
                logging.debug("Loaded custom workers")
        except IOError:
            logging.debug("Couldn't load workers.json, falling back to default (localhost) worker.")
