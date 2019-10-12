from github3 import GitHub

from github_webhook_handler.webhook_handlers import GitHubEventHandler
from jeeves import settings


class InstallationRepositoriesEventHandler(GitHubEventHandler):
    user_model = settings.AUTH_USER_MODEL

    def __init__(self, payload: dict, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        pass
