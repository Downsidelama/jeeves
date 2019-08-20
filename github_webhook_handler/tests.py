import json

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase, Client
from django.urls import reverse

from github_webhook_handler.webhook_distributor import WebhookDistributor


class GithubWebhookHandlerTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        pass

    def parse_json_string(self, input_string):
        return json.loads(input_string)

    def test_bad_request_returns_error(self):
        response = self.client.get('/event_handler')
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         self.parse_json_string(response.content.decode()))

    def test_correct_header_no_handler(self):
        response = self.client.get('/event_handler', {'X-GitHub-Event': 'true'})
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         self.parse_json_string(response.content.decode()))

    def test_push_event_returns_correct_response(self):
        response = self.client.get('/event_handler', **{'X-GitHub-Event': 'push'})
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         self.parse_json_string(response.content.decode()))
