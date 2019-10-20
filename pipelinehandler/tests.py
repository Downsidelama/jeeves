from django.test import TestCase

# Create your tests here.
from pipelinehandler.pipeline_script_parser import PipeLineScriptParser


class TestPipeLineScriptParser(TestCase):

    def test_yaml_has_invalid_key_raises_exception(self):
        with self.assertRaises(ValueError):
            PipeLineScriptParser().parse("before_install: true\r\nfuck_me: true")

    def test_yaml_is_correct_returns_parsed_dict_with_correct_values(self):
        expected_results = {
            'before_install': 'pip install -r requirements.txt',
            'script': 'python unittest discover',
            'after_install': 'coverage',
        }

        input_yaml = 'before_install: "pip install -r requirements.txt"\r\n' \
                     'script: "python unittest discover"\r\n' \
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
