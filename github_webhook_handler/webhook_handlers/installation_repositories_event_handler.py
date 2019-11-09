import logging

from django.contrib.auth import get_user_model

from dashboard.models import PipeLine
from github_webhook_handler.webhook_handlers import GitHubEventHandler
from jeeves import settings


class InstallationRepositoriesEventHandler(GitHubEventHandler):
    user_model = settings.AUTH_USER_MODEL

    def __init__(self, payload: dict, response: dict):
        super().__init__(payload, response)

    def _handle_event(self):
        try:
            action = self.payload['action']
            if action in ['added', 'removed']:
                repositories_added = self.payload['repositories_added']
                repositories_removed = self.payload['repositories_removed']
                user = get_user_model().objects.get(username=self.username)

                self._add_repositories(repositories_added, user)
                self._deactivate_repositories(repositories_removed)
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)
            self._set_response('ERROR', "Invalid payload")

    def _add_repositories(self, repositories_added, user):
        for repository in repositories_added:
            name = repository['name']
            repository_id = repository['id']
            repo_url = 'https://github.com/{}'.format(repository['full_name'])
            description = "Automatically generated pipeline for {}".format(repository['full_name'])
            pipelines = PipeLine.objects.filter(repository_id=repository_id)
            if len(pipelines) == 0:
                repo = self._register_repository(user=user, name=name, repository_id=repository_id, repo_url=repo_url,
                                                 description=description)
                logging.debug("Adding repository: {} with ID: {}".format(repo.name, repo.pk))
            else:
                pipelines[0].is_active = True
                pipelines[0].save()
                logging.debug("This repository is already in the database.")

    def _deactivate_repositories(self, repositories_removed):
        for repository in repositories_removed:
            repository_id = repository['id']
            pipelines = PipeLine.objects.filter(repository_id=repository_id)
            if len(pipelines) > 0:
                pipelines[0].is_active = False
                pipelines[0].save()
