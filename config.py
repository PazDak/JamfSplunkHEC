"""

"""

import json


class CONFIG():
    settings: dict

    def __init__(self):
        with open('config.json', 'r') as fp:
            self.settings = json.loads(fp.read())

    def create_config_file(self):
        """
        This Function will Create the Configuration file with the minimal requirements to function
        :return:
        """

    def save_settings(self) -> bool:
        with open('config.json', 'w+') as fp:
            fp.write(json.dumps(self.settings, indent=2, sort_keys=True))
        return True
