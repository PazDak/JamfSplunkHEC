# JamfSplunkHEC
This is a service that allows you to sync Jamf Pro events to a Splunk HEC Endpoint.
# Run setup.py
After creating a virtual environment pull the requirements from pip.
`pip install requirements.txt`

`python3 setup.py`
This will ask you several questions such as if you want to exclude non managed devices, how long since contacted, what sections to include.

Example config.json
```
{
  "args": {
    "days_since_contact": "0",
    "event_time_format": "timeAsScript",
    "excludeNoneManaged": false,
    "host_as_device_name": true,
    "jss_password": "<Your Jamf Pro Service Account token>",
    "jss_url": "<Your Jamf Pro Server>",
    "jss_username": "<Your Jamf Pro Service Account>",
    "sections": [
      "DISK_ENCRYPTION",
      "PURCHASING",
      "APPLICATIONS",
      "STORAGE",
      "PRINTERS",
      "LOCAL_USER_ACCOUNTS",
      "CERTIFICATES",
      "SECURITY",
      "OPERATING_SYSTEM",
      "LICENSED_SOFTWARE",
      "SOFTWARE_UPDATES",
      "EXTENSION_ATTRIBUTES",
      "GROUP_MEMBERSHIPS",
      "HARDWARE"
    ]
  },
  "splunk": {
    "splunkToken": "<Your HEC Token>",
    "splunkURL": "<yourSplunkServer>/services/collector/event"
  }
}
```

# Run the script

`python3 main.py`

# There is No Step 3
