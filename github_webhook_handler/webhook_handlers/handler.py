from django.http import HttpRequest
from abc import ABC, abstractmethod
from github3 import GitHub


class Handler:

    def __init__(self, payload: dict, response: dict, github_client: GitHub):
        self.payload = payload
        self.response = response
        self.github_client = github_client
        self._handle_event()

    @abstractmethod
    def _handle_event(self):
        pass

    def get_response(self):
        return self.response
