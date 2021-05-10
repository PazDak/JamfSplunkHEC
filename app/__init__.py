import json

from .models import devices
from .jamfTools import JamfTools
from .splunk import SplunkTools


class APP:
    def __init__(self, settings={}):
        print(json.dumps(settings, indent=2))
        self.jss = JamfTools.JamfPro(jamf_url=settings['jss']['hostname'],
                                     jamf_username=settings['jss']['username'],
                                     jamf_password=settings['jss']['password'])

        self.splunk_hec = SplunkTools.SplunkTools(host=settings['splunk']['hostname'],
                                                  splunk_token=settings['splunk']['hec_token'])

    def get_computer(self, jss_id=0):
        print("getting computer")
        results = self.jss.getComputerDetails(jss_id=jss_id)
        computer = devices.JamfComputer()
        computer.set_from_uapi(results)
        return computer

