import json
import datetime

from .models import devices
from .jamfTools import JamfTools
from .splunk import SplunkTools
from .device_checkpoint import CheckPoint

class APP:
    def __init__(self, settings={}):
        self.jss = JamfTools.JamfPro(jamf_url=settings['jss']['hostname'],
                                     jamf_username=settings['jss']['username'],
                                     jamf_password=settings['jss']['password'])

        self.splunk_hec = SplunkTools.SplunkTools(host=settings['splunk']['hostname'],
                                                  splunk_token=settings['splunk']['hec_token'])
        self.check_point = CheckPoint()

    def get_computer(self, jss_id=0):
        computer_meta_prior, computer_details_prior = self.check_point.get_computer(jss_id=jss_id)
        results = self.jss.getComputerDetails(jss_id=jss_id)
        computer = devices.JamfComputer()
        computer.set_from_uapi(results)
        return computer

    def get_all_computers(self, filters={}, sections=[], method="lastContactTime"):
        if method == "lastContactTime":
            return self.jss.getAllComputers(filters=filters,
                                            sections=sections,
                                            sortKey="&sort=general.lastContactTime%3Adesc")

        if method == "lastReportTime":
            return self.jss.getAllComputers(filters=filters,
                                            sections=sections,
                                            sortKey="&sort=general.reportDate%3Adesc")

        return self.jss.getAllComputers(filters=filters,
                                        sections=sections,
                                        sortKey="&sort=id%3Adesc")

    def get_computer_contact_events(self, filters={}, sections=[]):

        computers = self.get_all_computers(filters=filters, sections=sections, method="lastContactTime")
        events = []
        for computer in computers:
            thisComputer = devices.JamfComputer()
            thisComputer.set_from_uapi(computer)
            computer_meta = thisComputer.get_computer_meta()
            event ={
                'time': computer_meta['lastContactEpoch'],
                'source': 'jssContactEvent',
                'sourcetype': '_json',
                'computer_meta': computer_meta,
                'host': computer_meta['name']
            }
            events.append(event)

        return events

    def get_computer_report_events(self, filters={}, sections=['GENERAL'], check_point=True):
        computers = self.get_all_computers(filters=filters, sections=sections, method="lastReportTime")
        events = []

        for computer in computers:
            thisComputer = devices.JamfComputer()
            thisComputer.set_from_uapi(computer)
            computer_meta = thisComputer.get_computer_meta()
            event = {
                'time': computer_meta['lastReportEpoch'],
                'source': 'jssReportEvent',
                'sourcetype': '_json',
                'computer_meta': computer_meta,
                'host': computer_meta['name']
            }
            events.append(event)
            meta_keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user','department', 'building', 'room']
            thisComputerEvents = thisComputer.splunk_hec_events(meta_keys=meta_keys, nameAsHost=True, timeAs="report")

            for event in thisComputerEvents:
                events.append(event)

            if check_point:
                self.update_computer_checkpoint(jss_id=computer_meta['id'],
                                                computer_meta=computer_meta,
                                                computer_details=thisComputer.details)

        return events

    def update_computer_checkpoint(self, jss_id=0, computer_meta={}, computer_details={}):
        """
        This function will update a computer to the CheckPoint System
        :param jss_id: INT or STR of Jamf Pro ID
        :param computer_meta: the dictionary of the computer_meta
        :param computer_details: the dictionary of the computer_details
        :return:
        """

        updated = self.check_point.write_computer(jss_id=jss_id,
                                                  computer_meta=computer_meta,
                                                  computer_details= computer_details)

    def get_computers(self, start_time):

        pass