import yaml


class PipeLineScriptParser:

    def parse(self, script):
        return yaml.safe_load(script)
