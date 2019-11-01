from github_webhook_handler.webhook_handlers.build_event_handler import BuildEventHandler


class PullRequestEventHandler(BuildEventHandler):

    def __init__(self, payload, response):
        super().__init__(payload, response)

    def _handle_event(self):
        pass
