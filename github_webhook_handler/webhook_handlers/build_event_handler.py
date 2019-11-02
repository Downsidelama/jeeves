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

    def __init__(self, payload, response):
        super().__init__(payload, response)
        self.repository = self.get_repository()

    def _setup(self):
        self.url_loader = urllib3.PoolManager()
        self._load_workers()
        self._make_installation_client()

        if self.github_client:
            self.repository = self.get_repository()
        else:
            self._set_response('ERROR', "Couldn't handle event")
            return
        self._handle_event()

    def set_ci_status(self, commit: str, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        try:
            self.repository.create_status(commit, status.value, context=context, description=description)
        except KeyError:
            self._set_response('ERROR', "Invalid payload")
            logging.exception("Invalid payload")

    def get_repository(self):
        try:
            return self.github_client.repository(self.payload['repository']['owner']['login'],
                                                 self.payload['repository']['name'])
        except KeyError:
            logging.exception("Invalid payload")

    def get_free_worker(self):
        return self.workers[0]  # TODO: get the on with the least load on them.

    def _load_workers(self):
        try:
            with open('workers.json', 'r') as f:
                self.workers = json.load(f)
                logging.debug("Loaded custom workers")
        except IOError:
            logging.debug("Couldn't load workers.json, falling back to default (localhost) worker.")
