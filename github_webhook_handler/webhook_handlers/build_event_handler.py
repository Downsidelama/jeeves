from abc import ABC

from github_webhook_handler.webhook_handlers import GitHubEventHandler


class BuildEventHandler(GitHubEventHandler, ABC):
    """Abstract class to be used as a super class for events which involve running a pipeline"""

    def __init__(self, payload, response):
        super().__init__(payload, response)
