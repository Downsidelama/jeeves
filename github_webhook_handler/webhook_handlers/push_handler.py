import os

from django.http import HttpRequest

from github_webhook_handler.github_event_status import GithubEventStatus
from . import Handler
from ..worker.worker import Worker


class PushHandler(Handler):

    def __init__(self, payload, response: dict, github_client):
        super().__init__(payload, response, github_client)

    def _handle_event(self):
        branch = self.payload['ref'].split('/')[-1]
        full_name = self.payload['repository']['full_name']
        worker = Worker(['git', 'clone', '--depth', '50', '--branch', branch, 'https://github.com/{}.git'.format(full_name),
                full_name], self.github_client)
        worker.run_ci()

        self.set_ci_status(status=GithubEventStatus.FAILURE)

        self.response['status'] = 'OK'
        self.response['message'] = 'CI finished.'
