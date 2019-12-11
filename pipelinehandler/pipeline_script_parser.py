import os

import yaml


class PipeLineScriptParser:
    """Parses the YAML script and also validates it's content."""

    current_directory = os.path.dirname(__file__)

    def parse(self, script):
        try:
            if script:
                with open(os.path.join(self.current_directory, 'jeeves.yml'), 'r') as f:
                    allowed_components = yaml.safe_load(f.read())
                user_script = yaml.safe_load(script)

                if not (set(user_script.keys()) <= set(allowed_components.keys())):
                    """Check if there is more root level keys than allowed."""
                    raise ValueError("Invalid YAML.")
                self.validate_yaml(allowed_components, user_script)

                return user_script
            else:
                raise ValueError("Invalid YAML.")
        except yaml.YAMLError as e:
            raise ValueError(str(e))

    def validate_yaml(self, allowed_components, user_script):
        """Recursively goes through the dicts and checks keys and values.
        :raises ``ValueError`` when it finds an incorrect key/value."""

        for key, value in allowed_components.items():
            if key in user_script:
                if isinstance(user_script[key], list):
                    if allowed_components[key] is not True:
                        if not (set(user_script[key]) <= set(allowed_components[key])):
                            raise ValueError("Invalid YAML. Key: {}".format(key))
                elif isinstance(user_script[key], dict):
                    if not (user_script[key].keys() <= allowed_components[key].keys()):
                        raise ValueError("Invalid YAML. Key: {}".format(key))
                    self.validate_yaml(allowed_components[key], user_script[key])
                else:
                    if allowed_components[key] is not True:
                        if user_script[key] not in allowed_components[key]:
                            raise ValueError("Invalid YAML. Key: {}".format(key))
