import subprocess
import uuid


class PipeLineCommandGenerator:

    def __init__(self, parsed_script, repository, branch='master'):
        self.parsed_script = parsed_script
        self.repository = repository
        self.branch = branch
        self.command = self._generate_command()

    def _generate_command(self):
        uid = uuid.uuid4()
        language = self.parsed_script['language']
        version = self.parsed_script[language][0] + '-alpine'  # TODO: support more
        commands_list = self._generate_pre_commands() + self.parsed_script['script']
        commands = ' && '.join(commands_list)
        command = f"docker run --name \"{uid}\" -it --rm {language}:{version} /bin/sh -c \"{commands}\""
        return command

    def get_command(self):
        return self.command

    def _generate_pre_commands(self):
        folder = self.repository.split('/')[-1]
        list_of_cmds = \
            ['apk add --no-cache git gcc libressl-dev musl-dev libffi-dev',
             'cd /root/',
             f'git clone {self.repository} --branch={self.branch} {folder}',
             f'cd {folder}',
             ]

        return list_of_cmds
