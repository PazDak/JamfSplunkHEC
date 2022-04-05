"""
This is a basic setup script to load the configurations for this application to launch
"""
import copy
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
staticValues = [
    {
        'name': 'event_time_format',
        'value': 'timeAsScript'
    },
    {
        'name': 'host_as_device_name',
        'value': True
    }
]
allSections = [
    {
        'name': 'DISK_ENCRYPTION',
        'displayName': 'Disk Encryption',
        'default': False,
        'description': ''
     },    {
        'name': 'PURCHASING',
        'displayName': 'Purchasing',
        'default': True,
        'description': ''
     },    {
        'name': 'APPLICATIONS',
        'displayName': 'Applications',
        'default': True,
        'description': ''
     },    {
        'name': 'STORAGE',
        'displayName': 'Disk Information',
        'default': False,
        'description': ''
     },    {
        'name': 'PRINTERS',
        'displayName': 'Printers',
        'default': False,
        'description': ''
     },    {
        'name': 'LOCAL_USER_ACCOUNTS',
        'displayName': 'Local User Accounts',
        'default': False,
        'description': ''
     },    {
        'name': 'CERTIFICATES',
        'displayName': 'Certificates',
        'default': False,
        'description': ''
     },    {
        'name': 'SECURITY',
        'displayName': 'Security',
        'default': True,
        'description': ''
     },    {
        'name': 'OPERATING_SYSTEM',
        'displayName': 'Operating System',
        'default': True,
        'description': ''
     },    {
        'name': 'LICENSED_SOFTWARE',
        'displayName': 'Licensed Software',
        'default': False,
        'description': ''
     },    {
        'name': 'SOFTWARE_UPDATES',
        'displayName': 'Software Updates',
        'default': False,
        'description': ''
     },    {
        'name': 'EXTENSION_ATTRIBUTES',
        'displayName': 'Extension Attributes',
        'default': True,
        'description': ''
     },    {
        'name': 'GROUP_MEMBERSHIPS',
        'displayName': 'Group Memberships',
        'default': True,
        'description': ''
     },{
        'name': 'HARDWARE',
        'displayName': 'Hardware',
        'default': True,
        'description': ''
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

    def updateSplunk(self):
        splunkURL = input("Splunk URL")
        splunkToken = input("Splunk HEC Token")

        self.settings.settings['splunk']['splunkURL'] = splunkURL
        self.settings.settings['splunk']['splunkToken'] = splunkToken
        self.settings.save_settings()

    def getStringField(self, inputDesc: str, validators: list) -> str:
        herlperText = inputDesc + ": "
        isValid = False
        while not isValid:
            value = input(herlperText)
            isValid, reason = self.validateStringField(value, validators)
            if not isValid:
                print(reason)
            if isValid:
                return value

    def getPasswordField(self,inputDesc: str, validators: list) -> str:
        herlperText = inputDesc + ": "
        isValid = False
        while not isValid:
            value = getpass.getpass(herlperText)
            isValid, reason = self.validateStringField(value, validators)
            if not isValid:
                print(reason)
            if isValid:
                return value

    def getIntField(self,inputDesc: str, validators: list) -> str:
        herlperText = inputDesc + ": "
        isValid = False
        while not isValid:
            value = input(herlperText)
            isValid, reason = self.validateIntField(value, validators)
            if not isValid:
                print(reason)
            if isValid:
                return int(value)

    def getBoolField(self, inputDesc: str, validators: list) -> str:
        herlperText = inputDesc + " (T/F): "
        isValid = False
        while not isValid:
            value = input(herlperText)
            isValid, reason = self.validateBoolField(value, validators)
            if not isValid:
                print(reason)
            if isValid:
                if value.lower() == "t":
                    return True
                if value.lower() == "f":
                    return False

    def getListField(self, inputDesc: str, validators: list):
        class listFields():
            fields = copy.deepcopy(allSections)
            currentFields = []
            def __init__(self):
                pass

            def removeAll(self):
                self.currentFields = []
                pass

            def removeOne(self):
                inputS = "Choices to delete, type response"
                for currentField in self.currentFields:
                    inputS += f"\n\t{currentField['name']}"
                inputS += "\nSelection? "
                choice = input(inputS)
                newFields = []
                foundMatch = False
                for currentField in self.currentFields:
                    if choice.upper() == currentField['name']:
                        print(f"removing choice {choice.upper()}")
                        foundMatch = True
                    else:
                        newFields.append(currentField)
                if foundMatch:
                    self.currentFields = newFields
                else:
                    print("Invalid Choice: Try Again")

            def addAll(self):
                results = []
                for field in self.fields:
                    results.append(field)
                self.currentFields = results

            def addOne(self):
                pass

            def addDefaults(self):
                for field in self.fields:
                    if field['default']:
                        self.currentFields.append(field)

            def getFields(self):
                results = []
                for currentField in self.currentFields:
                    results.append(currentField['name'])
                return results

            def rootChoice(self):
                done = False
                while not done:
                    print(self.getFields())
                    choice = input("Add Defaults (D)\nAdd All (A)\nAdd One (a)\nRemove All (R)\nRemove One (r)\nChoice? ")
                    validChoices = ['D', 'A', 'R', 'a', 'r']
                    if choice in validChoices:

                        if choice == "D":
                            self.addDefaults(),
                        if choice == "A":
                            self.addAll()
                        if choice == "a":
                            self.addOne()
                        if choice == "R":
                            self.removeAll()
                        if choice == "r":
                            self.removeOne()

                        anotherChoice = input("Repeat Choice? (T/F)")
                        if anotherChoice.lower() == "f":
                            done = True
                    else:
                        print("Invalid Response")
                pass
        fields = listFields()
        fields.rootChoice()
        return fields.getFields()

    def validateBoolField(self, value, validator_l):
        if value.lower() == "t":
            return True, None
        if value.lower() == "f":
            return True, None
        return False, "Not a Valid Bool"

    def validateIntField(self, value, validator_l):
        try:
            value = int(value)
        except ValueError:
            return False, "Not a valid int"
        response = []
        if validator_l.__len__() == 0:
            return True, None
        for validator in validator_l:
            if str(validator).__contains__("int:Greater:"):
                if value >= 0:
                    return True, None

        if response.__len__() == 0:
            return False, "Validators failed"
        return True, None

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
        for staticValue in staticValues:
            args[staticValue['name']] = staticValue['value']
        for requiredArg in requiredArgs:
            argValue = None
            if requiredArg['type'] == "str":
                argValue = self.getStringField(inputDesc=requiredArg['description'],
                                               validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue
            if requiredArg['type'] == "password":
                argValue = self.getPasswordField(inputDesc=requiredArg['description'],
                                                 validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue
            if requiredArg['type'] == "int":
                argValue = self.getIntField(inputDesc=requiredArg['description'],
                                            validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue
            if requiredArg['type'] == "bool":
                argValue = self.getBoolField(inputDesc=requiredArg['description'],
                                             validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue
            if requiredArg['type'] == "list:checked":
                print("here")
                argValue = self.getListField(inputDesc=requiredArg['description'],
                                             validators=requiredArg['validators'])
                args[requiredArg['name']] = argValue
            if argValue is None:
                print(requiredArg)
        print(json.dumps(args))
        self.settings.settings['args'] = args
        self.settings.save_settings()

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
    print("Setting up Modular Input:")
    app.updateArgs()
    print("-----\nSetting Up Splunk")
    app.updateSplunk()

