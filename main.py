"""
This Application will log to Splunk Computers that have inventoried in the previous time fram the previous time frame
"""
import json
import glob
import requests
import time
from datetime import datetime, timedelta, timezone

import app
from app.splunk import SplunkTools

from config import CONFIG

def get_contact_events(app, settings):
    settings['app']['collection']['contactEvents']['enabled']
    time_delta = settings['app']['collection']['contactEvents']['minutes']
    time_s = datetime.now(timezone.utc) - timedelta(minutes=time_delta)
    filters = {
        'lastContactTime':{
            'value': time_s.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'operator': '>'
        }
    }
    sections = ['GENERAL', 'HARDWARE', 'USER_AND_LOCATION']

    events = app.get_computer_contact_events(filters=filters, sections=sections)
    splunk = SplunkTools.SplunkTools(host=settings['splunk']['hostname'],
                                     splunk_token=settings['splunk']['hec_token'])
    for event in events:
        splunk.add_event(event)
    print(f"Contact Events: {splunk.get_events().__len__()}")
    splunk.write_batch_events(sync=False)

def get_report_events(app, settings):
    settings['app']['collection']['reportEvents']['enabled']
    time_delta = settings['app']['collection']['reportEvents']['minutes']
    time_s = datetime.now(timezone.utc) - timedelta(minutes=time_delta)
    filters = {
        'lastReportTime':{
            'value': time_s.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'operator': '>'
        }
    }

    allKeys = [
        "GENERAL",
        "DISK_ENCRYPTION",
        "PURCHASING",
        "APPLICATIONS",
        "STORAGE",
        "USER_AND_LOCATION",
        "PRINTERS",
        "HARDWARE",
        "LOCAL_USER_ACCOUNTS",
        "CERTIFICATES",
        "SECURITY",
        "OPERATING_SYSTEM",
        "LICENSED_SOFTWARE",
        "SOFTWARE_UPDATES",
        "EXTENSION_ATTRIBUTES",
        "GROUP_MEMBERSHIPS"
    ]

    events = app.get_computer_report_events(filters=filters, sections=allKeys)
    splunk = SplunkTools.SplunkTools(host=settings['splunk']['hostname'],
                                     splunk_token=settings['splunk']['hec_token'])

    for event in events:
        splunk.add_event(event)
    print(f"Report Events: {splunk.get_events().__len__()}")
    splunk.write_batch_events(sync=False)


if __name__ == "__main__":

    logs = []
    print("setting up Application")
    settings = CONFIG()

    run_app = True
    while run_app:
        try:
            startTime = time.time()
            settings = CONFIG()
            thisApp = app.APP(settings=settings.settings)

            print("running Application")
            # Application Start

            ## Jamf Pro Contact Events
            get_contact_events(app=thisApp, settings=settings.settings)
            print(f"finished Contact events at: {time.time()}")
            ## Jamf Pro Report Events
            get_report_events(app=thisApp, settings=settings.settings)
            print(f"finished Report events at: {time.time()}")
            print("cleaning up Application")
            del thisApp
            del settings
            endTime = time.time()
            print(endTime-startTime)
            sleepTime = (15*60-int(endTime-startTime)-15)
            print(int(sleepTime))
            print("Resetting Application and resting")
            if sleepTime < 0:
                sleepTime = 0
            time.sleep(sleepTime)
        except:
            sleepTime = 14*60
            print("sleeping, ran into a problem. Full Tear Down")
            time.sleep(sleepTime)
