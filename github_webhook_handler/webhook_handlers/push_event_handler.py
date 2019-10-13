import json
import logging

import urllib3

from dashboard.models import PipeLine
from github_webhook_handler.github_event_status import GithubEventStatus
from . import GitHubEventHandler


class PushEventHandler(GitHubEventHandler):
    workers = [  # Default worker, can be overwritten with workers.json file
        {
            "id": 1,
            "url": "http://localhost:8000/pipelinehandler/github-pipeline/"
        }
    ]
    config_file_url = 'https://raw.githubusercontent.com/{user}/{repo_name}/{revision}/.jeeves.yml'
    url_loader = urllib3.PoolManager()

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        self._load_workers()
        self._make_installation_client()

        if self.github_client:
            self.repository = self.get_repository()
        else:
            self._set_response('ERROR', "Couldn't handle event")
            return
        self.set_ci_status(status=GithubEventStatus.PENDING)

        self.send_to_worker()

    def _load_workers(self):
        try:
            with open('workers.json', 'r') as f:
                self.workers = json.load(f)
                logging.debug("Loaded custom workers")
        except IOError:
            logging.debug("Couldn't load workers.json, falling back to default (localhost) worker.")

    def send_to_worker(self):
        try:
            post_body = {
                'config_file_content': self._get_config_file_content(),
                'pipeline_id': PipeLine.objects.get(repository_id=self.payload['repository']['id']).pk,
                'commit_sha': self.payload['after'],
                'html_url': self.payload['repository']['html_url'],
                'installation_id': self.payload['installation']['id'],
                'ref': self.payload['ref'],
            }

            worker = self.get_free_worker()

            self.url_loader.request('POST', worker['url'], body=json.dumps(post_body))

            return True
        except (KeyError, ValueError):
            logging.exception("Couldn't handle event", exc_info=True)
            self._set_response('ERROR', "Couldn't handle event")
            return False

    def get_free_worker(self):
        return self.workers[0]  # TODO: get the on with the least load on them.

    def get_repository(self):
        try:
            return self.github_client.repository(self.payload['repository']['owner']['login'],
                                                 self.payload['repository']['name'])
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)

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

    def set_ci_status(self, commit: str = None, status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        try:
            if commit is None:
                commit = self.payload['after']
            self.repository.create_status(commit, status.value, context=context, description=description)
        except KeyError:
            self._set_response('ERROR', "Invalid payload")
            logging.exception("Invalid payload", exc_info=True)
