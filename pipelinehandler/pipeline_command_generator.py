import subprocess
import uuid


class PipeLineCommandGenerator:

    def __init__(self, parsed_script, repository, branch='master', revision=""):
        self.parsed_script = parsed_script
        self.repository = repository
        self.branch = branch
        self.revision = revision
        self.commands = self._generate_command()

    def _generate_command(self):
        cmds = []
        language = self.parsed_script['language']
        for current_version in self.parsed_script[language]:
            uid = str(uuid.uuid4())
            version = current_version + '-alpine'
            commands_list = self._generate_pre_commands() + self.parsed_script['script']
            commands = ' && '.join(commands_list)
            command = f"docker run --name {uid} -it --rm {language}:{version} /bin/sh -c".split(' ')
            command.append(commands)
            cmds.append(command)
        return cmds

    def get_commands(self):
        return self.commands

    def _generate_pre_commands(self):
        folder = self.repository.split('/')[-1]

        list_of_cmds = \
            ['apk add --no-cache git gcc libressl-dev musl-dev libffi-dev',
             'cd /root/',
             f'git clone {self.repository} --branch={self.branch} {folder}',
             f'cd {folder}',
             ]

        if self.revision != "":
            list_of_cmds += [f'git checkout -qf {self.revision}']

        return list_of_cmds
