"""
This is a basic setup script to load the configurations for this application to launch
"""
import getpass
import json
import os
import re
import validators
from config import CONFIG

requiredArgs = [
    {
        'name': 'jss_url',
        'description': 'Jamf Pro URL',
        'type': 'str',
        'validators': ['weburl'],
        'required': True,
        'allowNull': False
    },{
        'name': 'jss_username',
        'type': 'str',
        'description': 'Jamf Pro Username',
        'validators': [],
        'required': True,
        'allowNull': False
    },{
        'name': 'jss_password',
        'type': 'password',
        'description': 'Jamf Pro Password',
        'validators': [],
        'required': True,
        'allowNull': False
    },{
        'name': 'days_since_contact',
        'type': 'int',
        'description': 'Days Since Contact (0 = Infinity)',
        'validators': ['int:Greater:0'],
        'required': True,
        'allowNull': False,
        'default': 1
    },{
        'name': 'excludeNoneManaged',
        'description': 'Exclude None Managed Devices',
        'type': 'bool',
        'validators': [],
        'required': True,
        'allowNull': False,
        'default': True
    },{
        'name': 'host_as_device_name',
        'type': 'bool',
        'description': '',
        'validators': [],
        'required': True,
        'allowNull': False,
        'default': 'time_as_script'
    },{
        'name': 'event_time_format',
        'type': "str",
        'description': '',
        'validators': ['eventTimeFormat'],
        'required': True,
        'allowNull': False
    },{
        'name': 'sections',
        'type': 'list:checked',
        'description': '',
        'validators': ['computer:sections:contained'],
        'required': True,
        'allowNull': False,
        'default': [{
            'name', ''
        }]
    }
]

class setup():
    def __init__(self):

        self.settings = CONFIG()
        print(self.settings.settings)

    def writeConfig(self,settings: dict):
        self.settings.save_settings()

    def get_current_settings(self,) -> dict:
        return self.settings.settings

    def main(self, update_jss="", update_kinobi="", update_splunk= ""):
        """
        Main function for launching the Setup Script
        :return:
        """
        if update_jss == "":
            update_jss = input("Update JSS? T/F")

        if update_jss.lower() == 't':
            self.__update_jss()

        if update_kinobi == "":
            update_kinobi = input("Update Kinobi? T/F")

        if update_kinobi.lower() == "t":
            self.__update_kinobi()

        if update_splunk == "":
            update_splunk = input("Update Splunk?")

        if update_splunk.lower() == "t":
            self.__update_splunk()

    def __update_app(self):
        """
        This is the setup script for this application
        """
        use_defaults = input("Use Defaults: T/F")
        if use_defaults.lower() == "t":
            app = {
                "freq_minutes": 15,
                "runOnce": False,
                "checkPointDevices": False,
                "collection": {
                    "contactEvents": {
                        "enabled": False,
                    },
                    "reportEvents": {
                        "enabled": True,
                        "fullInventory": True,
                        "diffInventory": False,
                        "processAlerts": False,
                        "removeKeys": ['fonts', 'services', 'packageReceipts', 'contentCaching', 'ibeacons', 'plugins', 'attachments']
                    },
                    "alertEvents": [
                    ]
                }
            }
            self.settings.settings['app'] = app
            self.settings.save_settings()
            return None

    def __update_splunk(self):
        """
        This function will Update settings for the Splunk HEC connector
        """
        enable_splunk = input("Enable Splunk: T/F")
        if enable_splunk.lower() == "f":
            self.settings.settings['splunk'] = {"enabled": False}
            self.settings.save_settings()
            return None

        splunk_url = input("Splunk HEC Endpoint: ")
        splunk_HEC_token = input("Splunk HEC Token: ")
        splunk = {
            "hostname": splunk_url,
            "hec_token": splunk_HEC_token,
            "hec_config": {
                "keys": ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user',
                         'department', 'building', 'room'],
                "timeAsReport": True,
                "timeAsContact": False,
                "hostAsSource": True,

            }
        }
        self.settings.settings['splunk'] = splunk
        self.settings.save_settings()

    def __update_kinobi(self):
        """
        This function is used for updating the Kinobi Configuration
        """

        enable_kinobi = input("Enable Kinobi: T/F")

        if enable_kinobi.lower() == "f":
            self.settings.settings['kinobi'] = {"enabled": False}
            self.settings.save_settings()
            return None

        kinobi_url = input("Kinobi URL: ")
        kinobi_username = input("Kinobi Username: ")
        kinobi_password = getpass.getpass("Kinobi Password: ")
        kinobi = {
            "hostname": kinobi_url,
            "username": kinobi_username,
            "password": kinobi_password
        }

        self.settings.settings['kinobi'] = kinobi
        self.settings.save_settings()

    def __update_jss(self):

        jss_url = input("JSS URL: ")
        jss_username = input("JSS Username: ")
        jss_password = getpass.getpass('JSS Password :')

        jss = {
            'hostname': jss_url,
            'username': jss_username,
            'password': jss_password
        }
        self.settings.settings['jss'] = jss
        self.settings.save_settings()

    def __update_cve(self):
        print("This is a Beta CVE service. Contact kyle.pazandak@jamf.com for access to the system")
        jamfCVEUrl = input("Jamf CVE Feed URL")
        jamfCVEToken = input("Jamf CVE Feed Token")

    def getStringField(self, inputDesc: str, validators: list) -> str:
        herlperText = inputDesc + ": "
        isValid = False
        while not isValid:
            value = input(herlperText)
            isValid, reason = self.validateStringField(value, validators)
            if not isValid:
                print(reason)

    def validateStringField(self, value, validator_l):
        response = []
        if validator_l.__len__() == 0:
            return True, None
        for validator in validator_l:
            if validator == "weburl":
                response.append(self.validatorWebURL(value))
                aTest, Reason = self.validatorWebURL(value)
                if not aTest:
                    return aTest, Reason

        if response.__len__() == 0:
            return False, "Validators failed"

        return True, None

    def updateArgs(self):
        args = {}
        for requiredArg in requiredArgs:
            if requiredArg['type'] == "str":
                argValue = self.getStringField(inputDesc=requiredArg['description'], validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue


    @staticmethod
    def validatorWebURL(value):
        if value.__contains__("https://"):
            value = value.replace("https://","")
        if value.__contains__("http://"):
            value = value.replace("http://", "")

        if value[:-1] == "/":
            value = value[:-1]
        if validators.domain(value):
            return True, value
        else:
            print("invalid url type")
            return False, value


if __name__ == "__main__":
    """
    Main Run Function
    """
    app = setup()
    app.updateArgs()
