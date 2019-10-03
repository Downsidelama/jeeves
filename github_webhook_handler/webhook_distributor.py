import json
import os

import github3
from django.http import HttpRequest
from github_webhook_handler.webhook_handlers import Handler
from . import webhook_handlers
from dotenv import load_dotenv


class WebhookDistributor:

    def __init__(self, request: HttpRequest):
        self.request = request
        self.response = {'status': 'OK', 'message': ''}
        self._distribute()

    def _distribute(self):
        request = self.request
        if 'X-GitHub-Event' in request.headers:
            self._load_env()
            payload = self._load_body_as_json(request.body)
            print(json.dumps(payload, indent=4, sort_keys=True))
            github_client = self._create_installation_client(payload['installation']['id'])
            handler: Handler = None

            if request.headers['X-GitHub-Event'] == 'push':
                print('push event')
                handler = webhook_handlers.PushHandler(payload, self.response, github_client)

            if handler:
                self.response = handler.get_response()
            else:
                self.response['status'] = 'error'
                self.response['message'] = 'No handler for this hook.'
        else:
            self.response['status'] = 'error'
            self.response['message'] = 'Invalid request.'

    def _load_env(self):
        load_dotenv()

    def _create_installation_client(self, installation_id):
        GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
        GITHUB_APP_IDENTIFIER = os.getenv('GITHUB_APP_IDENTIFIER')

        client = github3.GitHub()
        client.login_as_app_installation(GITHUB_PRIVATE_KEY.encode(), GITHUB_APP_IDENTIFIER, installation_id)

        return client

    def get_response(self) -> dict:
        return self.response

    def _load_body_as_json(self, body):
        return json.loads(body.decode())
