from github_webhook_handler.webhook_handlers import GitHubEventHandler
from jeeves import settings


class InstallationEventHandler(GitHubEventHandler):

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        pass
