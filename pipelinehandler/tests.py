import json
from unittest import mock

from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse

from pipelinehandler.pipeline_command_generator import PipeLineCommandGenerator
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class TestPipeLineScriptParser(TestCase):

    def test_yaml_has_invalid_key_raises_exception(self):
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse("before_install: true\r\nfuck_me: true")

    def test_yaml_is_correct_returns_parsed_dict_with_correct_values(self):
        expected_results = {
            'before_install': 'pip install -r requirements.txt',
            'script': ['python unittest discover', 'python something'],
            'after_install': 'coverage',
        }

        input_yaml = 'before_install: "pip install -r requirements.txt"\r\n' \
                     'script:\r\n' \
                     '  - "python unittest discover"\r\n' \
                     '  - "python something"\r\n' \
                     'after_install: "coverage"'

        output_yaml = PipeLineScriptParser().parse(input_yaml)
        self.assertEquals(expected_results, output_yaml)

    def test_empty_yaml_raises_exception(self):
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse("")

    def test_invalid_yaml_raises_exception(self):
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse("string:\r\naaaaa")

    def test_sub_values_are_invalid_raises_exception(self):
        input_yaml = 'python: "3.7"\r\naddons:\r\n  firefox:\r\n        - "invalid_version"'
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse(input_yaml)

        input_yaml = 'python: "invalid_version"\r\naddons:\r\n  firefox:\r\n        - "60.0"'
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse(input_yaml)

        input_yaml = 'addons:\r\n   chrome:\r\n     - "60.0"'
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse(input_yaml)


class TestPipeLineCommandGenerator(TestCase):

    def test_pull_request_correct_input(self):
        parsed_script = {
            "language": "python",
            "python": ['3.7'],
            'script': ['python manage.py test'],
        }
        command = PipeLineCommandGenerator(parsed_script,
                                           'https://github.com/Test/Repository', number=1).get_commands()

        self.assertTrue(any('git clone https://github.com/Test/Repository' in text for text in command[0]) and
                        any('python:3.7' in text for text in command[0]) and
                        any('python manage.py test' in text for text in command[0]))

    def test_multiple_language_version_multiple_elements_in_array(self):
        parsed_script = {
            "language": "python",
            "python": ['3.7', '3.6'],
            'script': ['python manage.py test'],
        }

        command = PipeLineCommandGenerator(parsed_script,
                                           'https://github.com/Test/Repository', branch='master',
                                           revision='revision').get_commands()

        self.assertEquals(2, len(command))

    def test_branch_and_revision_in_command(self):
        parsed_script = {
            "language": "python",
            "python": ['3.7', '3.6'],
            'script': ['python manage.py test'],
        }
        command = PipeLineCommandGenerator(parsed_script,
                                           'https://github.com/Test/Repository', branch='master',
                                           revision='revision').get_commands()

        self.assertTrue(any('--branch=master' in text for text in command[0]) and
                        any('git checkout -qf revision' in text for text in command[0]))


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    @mock.patch('pipelinehandler.views.PipeLineRunner')
    @mock.patch('pipelinehandler.views.get_object_or_404')
    def test_github_pipeline_handler_pull_request_call_correct_parameters(self, get_mock, pipeline_runner_mock):
        data = {
            'config_file_content': "language: python",
            'pipeline_id': 1,
            'commit_sha': "0000000000000000000000000000000000000000",
            'html_url': "https://github.com/Test/Repository",
            'installation_id': 1,
            'ref': "important_feature",
            'number': 1,
        }
        self.client.post(reverse('pipelinehandler:github-handler'), json.dumps(data), content_type='application/json')

        self.assertEquals(pipeline_runner_mock.call_args[1],
                          {'revision': data['commit_sha'], 'installation_id': data['installation_id'],
                           'pull_request_number': data['number']})
        self.assertEquals(pipeline_runner_mock.call_args[0], (get_mock(1),))

    @mock.patch('pipelinehandler.views.PipeLineRunner')
    @mock.patch('pipelinehandler.views.get_object_or_404')
    def test_github_pipeline_handler_push_call_correct_parameters(self, get_mock, pipeline_runner_mock):
        data = {
            'config_file_content': "language: python",
            'pipeline_id': 1,
            'commit_sha': "0000000000000000000000000000000000000000",
            'html_url': "https://github.com/Test/Repository",
            'installation_id': 1,
            'ref': "important_feature",
        }

        self.client.post(reverse('pipelinehandler:github-handler'), json.dumps(data), content_type='application/json')
        self.assertEquals(pipeline_runner_mock.call_args[1],
                          {'revision': '0000000000000000000000000000000000000000', 'installation_id': 1,
                           'branch': 'important_feature'})
        self.assertEquals(pipeline_runner_mock.call_args[0], (get_mock(1),))

    @mock.patch('pipelinehandler.views.PipeLineRunner')
    @mock.patch('pipelinehandler.views.get_object_or_404')
    def test_github_pipeline_exception_no_call_to_pipeline_runner(self, get_mock, pipeline_runner_mock):
        self.client.post(reverse('pipelinehandler:github-handler'), content_type='application/json')

        self.assertEquals(pipeline_runner_mock.call_count, 0)
