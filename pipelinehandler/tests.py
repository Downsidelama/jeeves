from django.test import TestCase

# Create your tests here.
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

        self.assertIn('git clone https://github.com/Test/Repository', command[0])
        self.assertIn('python:3.7', command[0])
        self.assertIn('python manage.py test', command[0])

    def test_multiple_language_version_multiple_elements_in_array(self):
        parsed_script = {
            "language": "python",
            "python": ['3.7', '3.6'],
            'script': ['python manage.py test'],
        }

        command = PipeLineCommandGenerator(parsed_script,
                                           'https://github.com/Test/Repository', number=1).get_commands()

        self.assertEquals(2, len(command))
