"""

"""

import json


class CONFIG():
    settings: dict

    def __init__(self):
        try:
            with open('config.json', 'r') as fp:
                self.settings = json.loads(fp.read())
        except FileNotFoundError:
            self.settings = self.create_config_file()

    def create_config_file(self):
        """
        This Function will Create the Configuration file with the minimal requirements to function
        :return:
        """
        newSettings = {}

        return newSettings

    def save_settings(self) -> bool:
        with open('config.json', 'w+') as fp:
            fp.write(json.dumps(self.settings, indent=2, sort_keys=True))
        return True
