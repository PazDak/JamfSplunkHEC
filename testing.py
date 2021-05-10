import json
import glob
import requests
import time

import app
from app.splunk import SplunkTools
from config import CONFIG

if __name__ == "__main__":
    logs = []
    print("setting up Application")
    settings = CONFIG()
    thisApp = app.APP(settings=settings.settings)

    computer = thisApp.get_computer(jss_id=4741)
    keys = ['supervised', 'managed', 'name', 'serial_number', 'udid', 'id', 'assigned_user','department', 'building', 'room']
    splunk_events = computer.splunk_hec_events(meta_keys=keys)
    splunk = SplunkTools.SplunkTools(host=settings.settings['splunk']['hostname'], splunk_token=settings.settings['splunk']['hec_token'])

    print(json.dump)
    for event in splunk_events:
        splunk.add_event(event=event)
    with open("files/splunk_events.json" , "w+") as fp:
        fp.write(json.dumps(splunk.events, indent=2))
    #splunk.write_batch_events()

    # Next Step is to rip apart the DISKs sections

