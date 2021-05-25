import json
from datetime import datetime, timedelta, timezone
import logging
import requests
import time


class JamfPro:

    class JamfUAPIAuthToken(object):
        def __init__(self, jamf_url, username, password):
            """
            :param jamf_url: Jamf Pro URL
            :type jamf_url: str
            :param username: Username for authenticating to JSS
            :param password: Password for the provided user
            """

            self.server_url = jamf_url
            self._auth = (username, password)
            self._token = ''
            self._token_expires = float()
            self.get_token()

        @staticmethod
        def unix_timestamp():
            """Returns a UTC Unix timestamp for the current time"""
            epoch = datetime(1970, 1, 1)
            now = datetime.utcnow()
            return (now - epoch).total_seconds()

        def headers(self, add=None):
            """
            :param add: Dictionary of headers to add to the default header
            :type add: dict
            """
            header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            if hasattr(self, '_auth_token'):
                header.update(self._auth_token.header)

            if add:
                header.update(add)

            return header

        @property
        def token(self):
            if (self._token_expires - self.unix_timestamp()) < 0:
                logging.warning("JSSAuthToken has expired: Getting new token")
                self.get_token()
            elif (self._token_expires - self.unix_timestamp()) / 60 < 5:
                logging.info("JSSAuthToken will expire soon: Refreshing")
                self.refresh_token()

            return self._token

        @token.setter
        def token(self, new_token):
            self._token = new_token

        @property
        def header(self):
            return {'Authorization': 'Bearer {}'.format(self.token)}

        def __repr__(self):
            return "<JSSAuthToken(username='{}')>".format(self._auth[0])

        def get_token(self):
            url = self.server_url + 'uapi/auth/tokens'
            logging.info("JSSAuthToken requesting new token")
            response = requests.post(url, auth=self._auth)
            if response.status_code != 200:
                raise Exception

            self._set_token(response.json()['token'], response.json()['expires'])

        def refresh_token(self):
            url = self.server_url + 'uapi/v1/auth/keepAlive'
            logging.info("JSSAuthToken attempting to refresh existing token")
            response = requests.post(url, headers=self.headers())
            if response.status_code != 200:
                logging.warning("JSSAuthToken is expired: Getting new token")
                self.get_token()

            self._set_token(response.json()['token'], response.json()['expires'])

        def _set_token(self, token, expires):
            """
            :param token:
            :type token: str
            :param expires:
            :type expires: int
            """
            self.token = token
            self._token_expires = float(expires) / 1000

        def about_token(self):
            url = self.server_url + 'uapi/v1/auth'
            response = requests.get(url, headers=self.headers())
            return response.json()

    def __init__(self, jamf_url="", jamf_username="", jamf_password=""):
        self.url=jamf_url
        self.username = jamf_username
        self.password = jamf_password
        self._authToken = self.JamfUAPIAuthToken(jamf_url=jamf_url, username=jamf_username, password=jamf_password)
        self.headers = {
            'Accept': 'application/json',
            'Authorization': self._authToken.header['Authorization'],
            }

    def _url_get_call(self, URL=""):
        """

        :param URL:
        :return:
        """
        url = URL
        payload = ""
        response = requests.request("GET", url, headers=self.headers, data=payload)
        response_dict = json.loads(response.content)
        if response.status_code !=200:
            print(response.content)
        return response_dict


    def _url_get_call_JSSResource(self, URL=""):
        """

        :param URL:
        :return:
        """
        headers = {
            'Accept': 'application/json',
        }
        url = URL
        payload = ""
        response = requests.request("GET", url, headers=self.headers, auth=(self.username, self.password), data=payload)
        response_dict = json.loads(response.content)
        return response_dict

    def _filter_computer(self, filters={}, computer={})-> bool:
        """
        Returns if to include the computer or not
        :param filters: Dictionary of the Filters for a Device
        :param computer: UAPI Computer Details
        :return: Boolean, Reason for False
        """
        # Device Managed
        if 'managed' in filters:
            if computer['general']['remoteManagement']['managed'] != filters['managed']['value']:
                return False, "notManaged"

        # Last Contact
        if 'lastContactTime' in filters:
            try:
                computerTime = datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                computerTime = datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%SZ")

            testTime = datetime.strptime(filters['lastContactTime']['value'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if filters['lastContactTime']['operator'] == '>':
                if computerTime > testTime:
                    pass
                else:
                    return False, "contactTimeBoundary"

        # Last Report
        if 'lastReportTime' in filters:
            try:
                if computer['general']['reportDate'] == None:
                    return False, "NoReportDate"
                computerTime = datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                computerTime = datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%SZ")

            testTime = datetime.strptime(filters['lastReportTime']['value'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if filters['lastReportTime']['operator'] == '>':
                if computerTime > testTime:
                    pass
                else:
                    return False, "reportTimeBoundary"

        # Base Case, Never got a False
        return True, None

    def _build_url(self, sections=[], page_number=1, page_size=200, endpoint="", sortKey=""):
        response = self.url
        response = response + endpoint
        section_s = "?"
        for section in sections:
            if section ==sections[0]:
                section_s = section_s + f"section={section}"
            else:
                section_s = section_s + f"&section={section}"
        response = response + section_s
        response = response + f"&page={page_number}&page-size={page_size}"
        if sortKey != "":
            response = response + sortKey
        return response

    def getAllComputers(self, filters: dict, sections: list, sortKey:str):
        endpoint = "uapi/v1/computers-inventory"
        page_number = 0
        page_size = 200
        another_page = True
        computers = []

        while another_page:
            url = self._build_url(sections=sections, page_size=page_size, page_number=page_number, endpoint=endpoint, sortKey=sortKey)
            print(url)
            p_computers = self._url_get_call(URL=url)['results']
            if p_computers.__len__() == 0:
                print("not getting another page")
                another_page = False
            else:
                for computer in p_computers:
                    addComputer, reason = self._filter_computer(filters=filters, computer=computer)
                    if addComputer:
                        computers.append(computer)
                    else:
                        if reason == "contactTimeBoundary":
                            another_page = False
                        if reason == "reportTimeBoundary":
                            another_page = False

                page_number = page_number + 1
        return computers

    def getComputerDetails(self, jss_id=0, ssn=""):
        """
        This function will return Current Details about a computer
        :param jss_id: INT jss_ID
        :param ssn: String of the SSN
        :return: JSON/DICT of the Computer
        """

        if jss_id > 0 and ssn == "":
            endpoint = f"uapi/v1/computers-inventory-detail/{jss_id}"
            response = self._url_get_call(URL=self.url+endpoint)
            return response

    def getComputerApplicationUsage(self, jss_id=0, days=21, appName=""):
        tod = datetime.now()
        d = timedelta(days=days)
        a = tod - d
        start = a.strftime("%Y-%m-%d")
        end = tod.strftime("%Y-%m-%d")

        endpoint = f"JSSResource/computerapplicationusage/id/{jss_id}/{start}_{end}"
        response = self._url_get_call_JSSResource(URL=self.url+endpoint)
        if appName != "":
            # Strip out other Applications
            for appUsageDay in response['computer_application_usage']:
                appUsageDay['apps'] = list(filter(lambda i: i['name'].lower() == appName, appUsageDay['apps']))

        return response
