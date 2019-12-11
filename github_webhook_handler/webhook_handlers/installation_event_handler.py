import logging

from django.contrib.auth import get_user_model

from dashboard.models import PipeLine
from github_webhook_handler.webhook_handlers import GitHubEventHandler


class InstallationEventHandler(GitHubEventHandler):
    """Handles the installation event"""

    def __init__(self, payload, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        try:
            action = self.payload['action']
            if action == 'created':
                repositories = self.payload['repositories']
                user = get_user_model().objects.get(username=self.username)
                for repository in repositories:
                    name = repository['name']
                    repository_id = repository['id']
                    repo_url = 'https://github.com/{}'.format(repository['full_name'])
                    description = "Automatically generated pipeline for {}".format(repository['full_name'])
                    pipelines = PipeLine.objects.filter(repository_id=repository_id)

                    if len(pipelines) == 0:
                        repo = self._register_repository(user=user, name=name, repository_id=repository_id,
                                                         repo_url=repo_url, description=description)
                        logging.debug("Adding repository: {} with ID: {}".format(repo.name, repo.pk))
                    else:
                        logging.debug("This repository is already in the database.")
            elif action == 'deleted':
                # May be obsolete, since GitHub won't send any more webhooks after uninstall.
                pass

        except KeyError:
            logging.exception("Invalid payload", exc_info=True)
            self._set_response('ERROR', "Invalid payload")
