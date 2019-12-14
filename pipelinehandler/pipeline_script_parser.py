import os

import yaml


class PipeLineScriptParser:
    """Parses the YAML script and also validates it's content."""

    current_directory = os.path.dirname(__file__)
    mandatory_keys = ['script', 'language']

    def parse(self, script):
        try:
            if script:
                with open(os.path.join(self.current_directory, 'jeeves.yml'), 'r') as f:
                    allowed_components = yaml.safe_load(f.read())
                user_script = yaml.safe_load(script)

                if not (set(user_script.keys()) <= set(allowed_components.keys())):
                    """Check if there is more root level keys than allowed."""
                    raise ValueError("Unexpected key(s) in YAML.")
                self.validate_yaml(allowed_components, user_script)
                self.check_language_consistency(user_script)
                self.check_mandatory_keys(user_script)

                return user_script
            else:
                raise ValueError("Script is empty.")
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
                            raise ValueError("Unexpected list item in key: {}".format(key))
                elif isinstance(user_script[key], dict):
                    if not (user_script[key].keys() <= allowed_components[key].keys()):
                        raise ValueError("Invalid YAML. Key: {}".format(key))
                    self.validate_yaml(allowed_components[key], user_script[key])
                else:
                    if allowed_components[key] is not True:
                        if user_script[key] not in allowed_components[key]:
                            raise ValueError("Invalid YAML. Key: {}".format(key))

    def check_language_consistency(self, user_script):
        if "language" in user_script:
            if user_script["language"] not in user_script:
                raise ValueError("Inconsistent language usage.")
        else:
            raise ValueError("Language key is not present.")

    def check_mandatory_keys(self, user_script):
        for key in self.mandatory_keys:
            if key not in user_script:
                raise ValueError(f"Key not present: {key}")
