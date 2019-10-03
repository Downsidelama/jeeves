from django.http import HttpRequest
from abc import ABC, abstractmethod
from github3 import GitHub

from github_webhook_handler.github_event_status import GithubEventStatus


class Handler:

    def __init__(self, payload: dict, response: dict, github_client: GitHub):
        self.payload = payload
        self.response = response
        self.github_client = github_client
        self.repository = github_client.repository(payload['repository']['owner']['login'],
                                                   payload['repository']['name'])
        self._handle_event()

    @abstractmethod
    def _handle_event(self):
        pass

    def get_response(self):
        return self.response

    def set_ci_status(self, commit: str = "", status: GithubEventStatus = GithubEventStatus.SUCCESS,
                      context: str = "Jeeves-CI", description: str = ""):
        if commit == "":
            commit = self.payload['after']
        self.repository.create_status(commit, status.value, context=context, description=description)
