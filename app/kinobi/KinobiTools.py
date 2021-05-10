import json
import requests
import time

class KinobiTools():
    __hostname = ""
    __username = ""
    __password = ""

    __authToken = ""
    __authExpire = ""

    def __init__(self, hostname="", username="", password=""):
        self.__hostname = hostname
        self.__username = username
        self.__password = password

    def __update_auth(self):
        #ToDo Fix the Below $Username:$Password
        headers = {
            'Accept': 'application/json',
        }
        data = ""
        response = requests.post(url=f"https://patch.kinobi.io/v2/auth/tokens", headers=headers, data=data)
        auth = json.loads(response.text)
        self.__authToken = auth['token']
        self.__expires = auth['expires']

        return True

    def get_softwareTitles(self):
        titles = self.__api_call(endpoint="/v2/softwaretitles")
        return titles

    def __api_call(self, endpoint) -> dict:
        #ToDo Add the Time Check

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__authToken}',
        }
        response = requests.get(url=self.__hostname + endpoint, headers=headers, data="")
        return json.loads(response.content)

    def test_connection(self) -> bool:
        return self.__update_auth()
