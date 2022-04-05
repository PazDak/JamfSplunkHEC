import json
import requests
from config import CONFIG
from app.splunk import SplunkTools

class runJamfComputers():
    class helper():
        proxy = {}
        outPutIndex = {}
        args = {}
        def __init__(self, settings={}):
            self.args = settings
            pass

        @staticmethod
        def get_proxy():
            return {}

        def send_http_request(self, url= "", method="GET", headers={}, use_proxy=False, timeout=30, verify=True ,payload="str"):
            print(url)
            if method.lower() == "get":
                response = requests.get(url=url, headers=headers)
                #print(response.json())
                return response

            if method.lower() == "post":
                print(url)
                response = requests.post(url=url, headers=headers)
                return response

        def get_arg(self, argKey:str, argDefault):
            if argKey not in self.args:
                print(argKey)

                return argDefault
            else:
                return self.args[argKey]

        def get_output_index(self):
            return self.outPutIndex

        def new_event(self, data:str, source:str, time:int, host:str, sourcetype:str) -> dict:
            newEvent = {'event': json.loads(data), 'sourcetype': sourcetype}
            return newEvent

        def setArgs(self, newArgs):
            self.args = newArgs

    class ew():
        """
        This is the Event writer function
        """
        url = ""
        token = ""
        index = ""
        sourcetype = ""

        events = []

        def __init__(self, splunkURL:str, splunkToken:str):
            self.url = splunkURL
            self.token = splunkToken
            self.splunk = SplunkTools.SplunkTools(host=splunkURL, splunk_token=splunkToken)

        def write_event(self, event):
            self.splunk.add_event(event)

        def writeEvents(self):
            self.splunk.write_batch_events(batch_size=100, sync=True)


    def __init__(self):
        self.settings = CONFIG()
        print(self.settings.settings)
        pass

    def run(self):
        from app import jamfComputers
        thisHelper = self.helper(settings=self.settings.settings['args'])
        thisEW = self.ew(splunkURL=self.settings.settings['splunk']['splunkURL'],
                                                            splunkToken=self.settings.settings['splunk']['splunkToken'])

        collector = jamfComputers.collect_events(helper=thisHelper, ew=thisEW)
        print(thisEW.events.__len__())
        thisEW.writeEvents()

if __name__ == "__main__":
    runner = runJamfComputers()
    runner.run()
    pass

