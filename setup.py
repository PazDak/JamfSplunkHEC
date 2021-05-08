"""
This is a basic setup script to load the configurations for this application to launch
"""
import getpass
import json
import os

from config import CONFIG


class setup():
    def __init__(self):
        self.settings = CONFIG


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
            jss_url = input("JSS URL: ")
            jss_username = input("JSS Username: ")
            jss_password = getpass.getpass('JSS Password :')

            jss = {
                'hostname': jss_url,
                'username': jss_username,
                'password': jss_password
            }
            print(json.dumps(jss))
        pass

        if update_kinobi == "":
            update_kinobi = input("Update Kinobi? T/F")

        if update_kinobi.lower() == "t":
            kinobi_url = input("Kinobi URL: ")
            kinobi_username = input("Kinobi Username: ")
            kinobi_password = getpass.getpass("Kinobi Password: ")
            kinobi = {
                "hostname": kinobi_url,
                "username": kinobi_username,
                "password": kinobi_password
            }

        if update_splunk == "":
            update_splunk = input("Update Splunk?")

        if update_splunk.lower() == "t":
            splunk_url = input("Splunk HEC Endpoint: ")
            splunk_HEC_token = input("Splunk HEC Token: ")
            splunk = {
                "hostname": "https://http-inputs-jamf.splunkcloud.com/services/collector/event",
                "hec_token": "4051291E-2582-4F42-A761-29BC67214060"
            }
if __name__ == "__main__":
    setup.main()
