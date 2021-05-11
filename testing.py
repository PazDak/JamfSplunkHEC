import json
import glob
import requests
import time
from datetime import datetime, timedelta, timezone

import app
from app.splunk import SplunkTools
from config import CONFIG

deviceKeys =[
    "GENERAL",
]

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

if __name__ == "__main__":
    logs = []
    print("setting up Application")
    settings = CONFIG()
    thisApp = app.APP(settings=settings.settings)

    time = datetime.now(timezone.utc) - timedelta(minutes=15)
    filters = {'lastContactTime':{
        'value': time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        'operator': '>'
    }}
    thisApp.get_all_computers(filters=filters, sections= deviceKeys, last_contact_time=time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    #computer = thisApp.get_computer(jss_id=4741)

    # Need to add the last report epcoh
    #keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user','department', 'building', 'room']
    #splunk_events = computer.splunk_hec_events(meta_keys=keys)
    #splunk = SplunkTools.SplunkTools(host=settings.settings['splunk']['hostname'], splunk_token=settings.settings['splunk']['hec_token'])

    #print(computer.get_computer_meta())
    #print(computer.details)
    #thisApp.update_computer_checkpoint(jss_id=4741, computer_meta=computer.get_computer_meta(), computer_details=computer.details)
#    for event in splunk_events:
#        splunk.add_event(event=event)
#    with open("files/splunk_events.json" , "w+") as fp:
#        fp.write(json.dumps(splunk.events, indent=2))
    # splunk.write_batch_events()

    # Next Step is to rip apart the DISKs sections

