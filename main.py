"""
This Application will log to Splunk Computers that have inventoried in the previous time fram the previous time frame
"""
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
    app.APP(settings=settings.settings)

    print("running Application")
    #
    print("cleaning up Application")


    print("closing application")
