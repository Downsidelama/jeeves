import json
import os

import github3
from django.http import HttpRequest

from github_webhook_handler.webhook_content_validator import WebhookContentValidator
from github_webhook_handler.webhook_handlers import GitHubEventHandler
from . import webhook_handlers
from dotenv import load_dotenv


class WebhookDistributor:

    handlers = {
        'installation_repositories': webhook_handlers.InstallationRepositoriesEventHandler,
        'push': webhook_handlers.PushEventHandler,
    }

    def __init__(self, request: HttpRequest):
        self.request = request
        self.response = {'status': 'OK', 'message': ''}
        self._distribute()

    def _distribute(self):
        content_validator = WebhookContentValidator()
        if 'X-GitHub-Event' in self.request.headers:
            print(self.request.headers['X-GitHub-Event'])
            payload = self._load_body_as_json(self.request.body)
            if content_validator.validate(payload):
                print(json.dumps(payload, indent=4, sort_keys=True))  # TODO: Remove this after debug done

                handler: GitHubEventHandler = None

                x_github_event = self.request.headers['X-GitHub-Event']
                if x_github_event in self.handlers.keys():
                    handler = self.handlers[x_github_event](payload, self.response, github_client)

                if handler:
                    self.response = handler.get_response()
                else:
                    self.response['status'] = 'error'
                    self.response['message'] = 'No handler for this hook.'
        else:
            self.response['status'] = 'error'
            self.response['message'] = 'Invalid request.'



    def get_response(self) -> dict:
        return self.response

    def _load_body_as_json(self, body):
        return json.loads(body.decode())
