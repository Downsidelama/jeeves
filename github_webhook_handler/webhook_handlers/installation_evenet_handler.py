from github_webhook_handler.webhook_handlers import GitHubEventHandler
from jeeves import settings


class InstallationEventHandler(GitHubEventHandler):
    user_model = settings.AUTH_USER_MODEL

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)
        self._parse_important_info()

    def _handle_event(self):
        users = self.user_model.objects.filter(username=self.username)
        if len(users) == 0:
            #  We have to add this user to the site
            self.user_model.objects.create_user(username=self.username, password='', social_uid=self.user_id)

    def _parse_important_info(self):
        self.username = self.payload['installation']['account']['login']
        self.user_id = self.payload['installation']['account']['id']
