import json
import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from social_django.models import UserSocialAuth

from github_webhook_handler.webhook_content_validator import HMACValidator, WebhookContentValidator
from github_webhook_handler.webhook_handlers import GitHubEventHandler, PushEventHandler

push_handler_payload = {
    'repository': {
        'owner': {
            'login': 'test_user',
            'id': 1,
        }
    }
}

installation_payload = {
    'installation': {
        'account': {
            'login': 'test_user',
            'id': 1,
        }
    }
}


class GithubWebhookHandlerTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        pass

    def test_bad_request_returns_error(self):
        response = self.client.get('/event_handler')
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         json.loads(response.content.decode()))

    def test_correct_header_no_handler(self):
        response = self.client.get('/event_handler', {'X-GitHub-Event': 'true'})
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         json.loads(response.content.decode()))

    def test_push_event_returns_correct_response(self):
        response = self.client.get('/event_handler', **{'X-GitHub-Event': 'push'})
        self.assertEqual({'status': 'error', 'message': 'Invalid request.'},
                         json.loads(response.content.decode()))


class GitHubEventHandlerTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_empty_payload_username_and_id_is_default(self):
        eh = GitHubEventHandler({}, {})
        self.assertEquals(eh.username, "")
        self.assertEquals(eh.user_id, -1)

    def test_push_handler_payload_username_and_id_correct(self):
        eh = GitHubEventHandler(push_handler_payload, {})

        self.assertEquals(eh.user_id, 1)
        self.assertEquals(eh.username, 'test_user')

    def test_installation_handler_payload_username_and_id_correct(self):
        eh = GitHubEventHandler(installation_payload, {})

        self.assertEquals(eh.user_id, 1)
        self.assertEquals(eh.username, 'test_user')

    def test_response_stays_the_same(self):
        test_response = {'test': 123}
        eh = GitHubEventHandler({}, test_response)
        self.assertEquals(test_response, eh.get_response())

    def test_user_gets_added_to_database(self):
        eh = GitHubEventHandler(installation_payload, {})
        self.assertEquals(get_user_model().objects.get(username='test_user').username, 'test_user')
        self.assertEquals(len(UserSocialAuth.objects.all()), 1)

    def test_user_only_gets_added_once_to_the_database(self):
        GitHubEventHandler(installation_payload, {})
        GitHubEventHandler(push_handler_payload, {})

        self.assertEquals(len(get_user_model().objects.all()), 1)
        self.assertEquals(len(UserSocialAuth.objects.all()), 1)


class PushEventHandlerTest(TestCase):
    valid_push_handler_payload = {
        'after': '0000000000000000000000000000000000000000',
        'repository': {
            'id': 1,
            'name': 'test-repo',
            'full_name': 'test_user/test-repo',
            'private': False,
            'owner': {
                'login': 'test_user',
                'id': 1,
            }
        },

        'installation': {
            'id': 1,
        }
    }

    def setUp(self):
        self.client = Client()

    # def test_push_event_handler_empty_payload_error_in_response(self):
    #     ph = PushEventHandler({}, {})
    #     self.assertEquals(ph.get_response()['status'], 'ERROR')

    # @patch('github_webhook_handler.webhook_handlers.push_event_handler.urllib3')
    # def test_push_event_handler_valid_payload_everything_correct(self, urllib3_mock):
    #     ph = PushEventHandler(self.valid_push_handler_payload, {})


class TestHMACValidator(TestCase):
    def test_correct_input_valid(self):
        self.assertTrue(HMACValidator(b'secret', b'message', '0caf649feee4953d87bf903ac1176c45e028df16').validate())

    def test_incorrect_input_invalid(self):
        self.assertFalse(HMACValidator(b'secret', b'message1', '0caf649feee4953d87bf903ac1176c45e028df16').validate())

    def test_long_key_valid(self):
        self.assertTrue(
            HMACValidator(b'secretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecret',
                          b'message', 'efcbb64cb045019731ed651657f516350bfa5de3').validate())


class TestWebhookContentValidator(TestCase):
    def setUp(self):
        self.validator = WebhookContentValidator()
        os.putenv('GITHUB_WEBHOOK_SECRET', "SECRET")

    def test_correct_input_valid(self):
        self.assertTrue(
            self.validator.validate(message=b"TEST_MESSAGE", _hash='530fab7c50551671962b481424b6e5624c278512'))

    def test_incorrect_input_invalid(self):
        self.assertFalse(
            self.validator.validate(message=b"TEST_MESSAGE", _hash='530fab7c50551671962b481424b6e5624c278513'))
