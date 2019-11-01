import json
import logging

from dashboard.models import PipeLine
from github_webhook_handler.github_event_status import GithubEventStatus
from github_webhook_handler.webhook_handlers.build_event_handler import BuildEventHandler


class PushEventHandler(BuildEventHandler):
    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        self.send_to_worker()

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
