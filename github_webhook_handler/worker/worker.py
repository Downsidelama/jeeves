import os
import subprocess
import sys
import shutil
import time
from threading import Thread


class Worker:
    work_number = 0

    def __init__(self, git_command, github_client):
        self.git_command = git_command
        self.github_client = github_client

    def run_ci(self):
        thread = Thread(target=self.clone_repository)

    def clone_repository(self):
        working_path = os.path.join('jeeves_temp', str(self.work_number))
        self.work_number += 1
        while os.path.exists(working_path):
            working_path = os.path.join('jeeves_temp', str(self.work_number))
            self.work_number += 1
        os.makedirs(working_path)
        # process = subprocess.Popen(self.git_command, stdout=subprocess.PIPE, cwd=working_path)
        # for line in process.stdout:
        #     sys.stdout.write(line.decode())
        # process.wait()
        print('done {}'.format(working_path))
        time.sleep(1)
        shutil.rmtree(working_path)
