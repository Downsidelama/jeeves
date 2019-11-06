import json
import logging

from dashboard.models import PipeLine
from github_webhook_handler.github_event_status import GithubEventStatus
from github_webhook_handler.webhook_handlers.build_event_handler import BuildEventHandler
from github_webhook_handler.webhook_handlers.utils.config_file_retriever import ConfigFileRetriever


class PushEventHandler(BuildEventHandler):
    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        self.set_ci_status(context="Jeeves CI - Push", commit=self.payload['after'], status=GithubEventStatus.PENDING)
        self.send_to_worker()

    def send_to_worker(self):
        try:
            if self.payload['after'] != "0000000000000000000000000000000000000000":
                config_file_content = ConfigFileRetriever().get_push_style(self.payload['after'],
                                                                           self.payload['repository']['owner']['login'],
                                                                           self.payload['repository']['name'])
                post_body = {
                    'config_file_content': config_file_content,
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
