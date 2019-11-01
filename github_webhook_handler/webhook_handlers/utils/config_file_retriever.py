import logging

import urllib3


class ConfigFileRetriever:
    config_file_url_push = 'https://raw.githubusercontent.com/{user}/{repo_name}/{revision}/.jeeves.yml'
    url_loader = urllib3.PoolManager()

    def get_push_style(self, revision, user, repository_name):
        try:
            current_config = self.config_file_url_push.format(user=user, repo_name=repository_name, revision=revision)
            response: urllib3.HTTPResponse = self.url_loader.request('GET', current_config)

            if response.status == 200:
                yaml = response.data.decode()  # TODO: Make it safe (don't allow huge amounts of data)
            else:
                raise ValueError("Yaml file doesn't exists in the repository at this revision")
            return yaml
        except KeyError:
            logging.exception("Invalid payload", exc_info=True)
            return ''
