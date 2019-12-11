import json
import logging

from dashboard.models import PipeLine
from github_webhook_handler.github_event_status import GithubEventStatus
from github_webhook_handler.webhook_handlers.build_event_handler import BuildEventHandler
from github_webhook_handler.webhook_handlers.utils.config_file_retriever import ConfigFileRetriever


class PullRequestEventHandler(BuildEventHandler):
    """Handles the PullRequest event"""

    def __init__(self, payload, response):
        super().__init__(payload, response)

    def _handle_event(self):
        self.set_ci_status(commit=self.payload['pull_request']['head']['sha'], context="Jeeves CI - Pull Request", status=GithubEventStatus.PENDING)
        if self.payload['action'] in ['opened', 'synchronize']:
            self.send_to_worker()

    def send_to_worker(self):
        """Sends the job to a worker."""
        config_file_content = ConfigFileRetriever() \
            .get_push_style(self.payload['pull_request']['head']['sha'],
                            self.payload['pull_request']['head']['user']['login'],
                            self.payload['pull_request']['head']['repo']['name'])
        try:
            post_body = {
                'config_file_content': config_file_content,
                'pipeline_id': PipeLine.objects.get(repository_id=self.payload['repository']['id']).pk,
                'commit_sha': self.payload['pull_request']['head']['sha'],
                'html_url': self.payload['repository']['html_url'],
                'installation_id': self.payload['installation']['id'],
                'ref': self.payload['pull_request']['head']['ref'],
                'number': self.payload['pull_request']['number'],
            }

            worker = self.get_free_worker()

            self.url_loader.request('POST', worker['url'], body=json.dumps(post_body))
            logging.debug("Sent request to pipelinerunner")
            return True
        except (KeyError, ValueError):
            logging.exception("Couldn't handle event", exc_info=True)
            self._set_response('ERROR', "Couldn't handle event")
            return False
