import requests
class runJamfComputers():
    class helper():

        proxy = {}
        outPutIndex = {}
        def __init__(self, settings={}):
            pass

        @staticmethod
        def get_proxy():
            return {}

        def send_http_request(self, url: str, method:str, headers:dict, use_proxy:bool):
            if method.lower() == "get":
                response = requests.get(url=url, headers=headers)
                return response

            if method.lower() == "post":
                response = requests.post(url=url, headers=headers)
                return response

        def get_arg(self, argKey:str, argDefault:str):
            result = ""
            return result

        def get_output_index(self):
            return self.outPutIndex

        def new_event(self, data:str, source:str, time:int, host:str, sourcetype:str) -> dict:
            newEvent = {'someEvent'}
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

        def __init__(self, splunkURL:str, splunkToken:str, splunkIndex:str, splunkSourceType: str):
            self.url = splunkURL
            self.token = splunkToken
            self.index = splunkIndex
            self.sourcetype = splunkSourceType

        def write_event(self, event):
            print(event)

    def __init__(self):
        pass

    def run(self):
        print("running")


if __name__ == "__main__":
    runner = runJamfComputers()
    runner.run()
    pass

