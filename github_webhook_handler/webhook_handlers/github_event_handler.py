import os
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor

import github3
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from abc import abstractmethod
from dotenv import load_dotenv
from social_django.models import UserSocialAuth

from dashboard.models import PipeLine


class GitHubEventHandler:
    social_auth_extra_info = r'{{"auth_time": {auth_time}, "id": {id}, "expires": null, "login": "{login}", ' \
                             '"access_token": "", "token_type": "bearer"}} '
    executor = ThreadPoolExecutor(max_workers=3)

    def __init__(self, payload: dict, response: dict):
        self.payload = payload
        self.response = response
        self._retrieve_user_info()
        self._register_github_user()
        self._setup()

    def _setup(self):
        """Must call _handle_event() after setup steps!"""
        self._handle_event()

    @abstractmethod
    def _handle_event(self):
        pass

    def get_response(self):
        return self.response

    def _retrieve_user_info(self):
        """Retrieves the user info from the payload"""

        self.username = ''
        self.user_id = -1

        self._try_retrievers()

    def _try_retrievers(self):
        available_retrievers = [
            self._get_user_info_from_push_event,
            self._get_user_info_from_installation_event
        ]

        for retriever in available_retrievers:
            try:
                retriever()
                return
            except KeyError:
                pass
        self._set_response('ERROR', "Invalid payload")
        logging.info("Couldn't find any retriever for this event.")

    def _get_user_info_from_push_event(self):
        self.username = self.payload['repository']['owner']['login']
        self.user_id = self.payload['repository']['owner']['id']

    def _get_user_info_from_installation_event(self):
        """This retriever work on Installation and InstallationRepositoriesEvents too."""

        self.username = self.payload['installation']['account']['login']
        self.user_id = self.payload['installation']['account']['id']

    def _register_github_user(self):
        """Registers the owner of the webhook to the user's table."""

        if self.username:
            user_model = get_user_model()

            try:
                user_model.objects.get(username=self.username)
                logging.debug("User already registered")
            except ObjectDoesNotExist:
                logging.debug("Adding user to the database")
                user = user_model.objects.create_user(username=self.username, password='', social_uid=self.user_id)
                extra_data = self.social_auth_extra_info.format(auth_time=int(time.time()), id=self.user_id,
                                                                login=self.username)
                UserSocialAuth.objects.create(user=user, provider='github', uid=self.user_id,
                                              extra_data=extra_data).save()
        else:
            logging.debug("Couldn't register the user since info couldn't be loaded")

    def _make_installation_client(self):
        """Only call this method if the app has permission to access the installation.
            Failing to do so will result in an exception thrown.
        """
        try:
            self.github_client = self._create_installation_client(self.payload['installation']['id'])
        except KeyError:
            self.github_client = None
            self._set_response("ERROR", "Invalid payload")
            logging.exception("Invalid payload", exc_info=True)

    def _set_response(self, status, message):
        self.response['status'] = status
        self.response['message'] = message

    @staticmethod
    def _register_repository(user, name, repository_id, repo_url):
        pipeline = PipeLine.objects.create(user=user, name=name, is_github_pipeline=True,
                                           repository_id=repository_id, repo_url=repo_url)
        pipeline.save()
        return pipeline

    @staticmethod
    def _create_installation_client(installation_id):
        load_dotenv()
        GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY')
        GITHUB_APP_IDENTIFIER = os.getenv('GITHUB_APP_IDENTIFIER')

        client = github3.GitHub()
        client.login_as_app_installation(GITHUB_PRIVATE_KEY.encode(), GITHUB_APP_IDENTIFIER, installation_id)

        return client
