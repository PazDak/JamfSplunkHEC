import json
import glob
import requests
import time

import app

from config import CONFIG

if __name__ == "__main__":
    logs = []
    print("setting up Application")
    settings = CONFIG()
    thisApp = app.APP(settings=settings.settings)

    computer = thisApp.get_computer(jss_id=4741)
    keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user','department', 'building', 'room']
    splunk_events = computer.splunk_hec_events(meta_keys=keys)
    s = json.dumps(splunk_events.__len__())
    print(json.dumps(splunk_events.__len__(), indent=2))
    print(s.__len__())

    with open("files/splunk_events.json", "w+") as fp:
        fp.write(json.dumps(splunk_events, indent=2))
    # Next Step is to rip apart the DISKs sections

