"""
This Class holds the Device model classes
"""
import json
import datetime

from abc import ABC, abstractmethod

class device(ABC):
    @abstractmethod
    def set_from_uapi(self, details):
        pass

    @abstractmethod
    def splunk_hec_events(self):
        pass


class JamfComputer(device):
    """
    This is a model for a Jamf Computer
    """

    def set_from_uapi(self, details):
        self.details = details

    def splunk_hec_events(self, meta_keys=[], nameAsHost=True, timeAs="report"):
        thisDevice = self.details.copy()
        del_keys = ['fonts', 'services', 'packageReceipts', 'contentCaching', 'ibeacons', 'plugins','attachments']
        computer_meta = self.__build_splunk_meta(meta_keys=meta_keys)

        baseEvent = self.__extract_base_event(computer=thisDevice, timeAs=timeAs, nameAsHost=nameAsHost, source="jss_inventory")

        for key in del_keys:
            if key in thisDevice:
                del thisDevice[key]

        splunk_events = []

        # Create Contact Event
        contact_event = self.__extract_contact_event(computer=thisDevice)
        contact_event['computer_meta'] = computer_meta
        print(json.dumps(contact_event))
        splunk_events.append(contact_event)
        # Applications:
        apps = self.__extract_applications(computer=thisDevice)
        del thisDevice['applications']
        for app in apps:
            event = {
                'app': app,
                'computer_meta': computer_meta
            }
            splunk_events.append(event)

        # Configuration Profiles
        configProfiles = self.__extract_configProfiles(computer=thisDevice)
        del thisDevice['configurationProfiles']
        for configProfile in configProfiles:
            event = {
                'configProfile': configProfile,
                'computer_meta': computer_meta
            }
            splunk_events.append(event)

        # Local User Accounts
        localAccounts = self.__extract_local_accounts(computer=thisDevice)
        del thisDevice['localUserAccounts']
        for localAccount in localAccounts:
            event ={
                'configProfile': localAccount,
                'groupMembership': computer_meta
            }
            splunk_events.append(event)
        # Groups
        groupMemberships = self.__extract_groups(computer=thisDevice)
        del thisDevice['groupMemberships']
        for groupMembership in groupMemberships:
            event = {
                'configProfile': groupMembership,
                'groupMembership': computer_meta
            }
            splunk_events.append(event)
        # Certificates
        certificates = self.__extract_certificates(computer=thisDevice)
        del thisDevice['certificates']
        for certificate in certificates:
            event = {
                'certificate':  certificate,
                'computer_meta': computer_meta
            }
            splunk_events.append(event)

        # Storage Drives
        partitions = self.__extract_storage(computer=thisDevice)
        del thisDevice['storage']
        for partition in partitions:
            event = {
                'diskPartition': partition,
                'computer_meta': computer_meta
            }
            splunk_events.append(event)
        # Extension Attributes
        ea, thisDevice = self.__extract_EAs(computer=thisDevice)

        s = json.dumps(thisDevice)

        # Final Processing

        ## General
        event = {
            "computerGeneral":thisDevice['general'],
            'computer_meta': computer_meta
        }
        del thisDevice['general']
        splunk_events.append(event)

        ## DiskEncryption
        event = {
            "computerDiskEncryption": thisDevice['diskEncryption'],
            'computer_meta': computer_meta,
        }
        del thisDevice['diskEncryption']
        splunk_events.append(event)

        ## Purchasing
        event = {
            'purchasing': thisDevice['purchasing'],
            'computer_meta': computer_meta
        }
        del thisDevice['purchasing']
        splunk_events.append(event)

        ## userAndLocation
        event = {
            'userAndLocation': thisDevice['userAndLocation'],
            'computer_meta': computer_meta
        }
        del thisDevice['userAndLocation']
        splunk_events.append(event)

        ## printers
        event = {
            'printers': thisDevice['printers'],
            'computer_meta': computer_meta
        }
        del thisDevice['printers']
        splunk_events.append(event)
        ## hardware
        event = {
            "computerHardware": thisDevice['hardware'],
            "computer_meta": computer_meta
        }
        del thisDevice['hardware']
        splunk_events.append(event)

        ## security
        event = {
            "computerSecurity": thisDevice['security'],
            "computer_meta": computer_meta
        }
        del thisDevice['security']
        splunk_events.append(event)

        ## operatingSystem
        event = {
            'computerOS': thisDevice['operatingSystem'],
            "computer_meta": computer_meta
        }
        del thisDevice['operatingSystem']
        splunk_events.append(event)

        ## licensedSoftware
        event = {
            'computerLicensedSoftware': thisDevice['licensedSoftware'],
            'computer_meta': computer_meta
        }
        del thisDevice['licensedSoftware']
        splunk_events.append(event)

        ## softwareUpdates
        event = {
            'computerSoftwareUpdates': thisDevice['softwareUpdates'],
            'computer_meta': computer_meta
        }
        del thisDevice['softwareUpdates']
        splunk_events.append(event)

        # Final Cleanup
        del thisDevice
        final_events = []
        for event in splunk_events:
            for key in baseEvent:
                if key not in event:
                    event[key] = baseEvent[key]
            final_events.append(event)
            pass
        return final_events

    def __extract_contact_event(self, computer):
        time = datetime.datetime.strptime(computer['general']['lastContactTime'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=datetime.timezone.utc)
        event = {
            "source": "jssContact",
            "time": time.timestamp(),
            "event": "Device Contact Jamf Pro Server"
        }

        return event

    def __extract_base_event(self, computer, timeAs, nameAsHost, source):
        base_event = {
            'source': source,
            'sourcetype': "_json"
        }

        if nameAsHost:
            base_event['host'] = computer['general']['name']
        if timeAs == "report":
            time = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
            base_event['time'] = time.timestamp()
        if timeAs == "contact":
            time = datetime.datetime.strptime(computer['general']['reportDate'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
            base_event['lastContactTime'] = time.timestamp()
        return base_event

    def __extract_applications(self, computer):
        applications = computer['applications']
        delete_keys = ['sizeMegabytes','externalVersionId','updateAvailable']
        parsed_app_l = []
        for app in applications:
            for delete_key in delete_keys:
                if delete_key in app:
                    del app[delete_key]

            parsed_app_l.append(app)

        return parsed_app_l

    def __extract_configProfiles(self, computer):
        config_profiles = computer['configurationProfiles']
        del_keys = ["profileIdentifier",]
        config_profile_l = []
        for config_profile in config_profiles:
            # Delete Keys not needed
            for key in del_keys:
                if key in config_profile:
                    del config_profile[key]

            config_profile_l.append(config_profile)

        return config_profile_l

    def __extract_certificates(self, computer):
        certificates = computer['certificates']
        del_keys = []
        certificates_l = []
        for cert in certificates:
            # Delete Keys not needed
            for key in del_keys:
                if key in cert:
                    del cert[key]

            certificates_l.append(cert)

        return certificates_l

    def __extract_EAs(self, computer):
        ea_sub_keys = ['purchasing', 'general', 'userAndLocation', 'hardware', 'operatingSystem']
        del_keys = ['options', 'inputType', 'multiValue']
        extension_attribute_l = []
        for ea_key in ea_sub_keys:
            for EA in computer[ea_key]['extensionAttributes']:
                if EA['multiValue'] == False and EA['values'].__len__() ==1 :
                    EA['value'] = EA['values'][0]
                    del EA['values']
                for key in del_keys:
                    if key in EA:
                        del EA[key]
                extension_attribute_l.append(EA)
            del computer[ea_key]['extensionAttributes']

        for EA in computer['extensionAttributes']:
            if EA['multiValue'] == False and EA['values'].__len__() == 1:
                EA['value'] = EA['values'][0]
                del EA['values']
            for key in del_keys:
                if key in EA:
                    del EA[key]

            extension_attribute_l.append(EA)
        del computer['extensionAttributes']
        return extension_attribute_l, computer

    def __extract_groups(self, computer):
        groups = computer['groupMemberships']
        delete_keys = ['']
        parsed_groups_l = []
        for group in groups:
            for delete_key in delete_keys:
                if delete_key in group:
                    del group[delete_key]

            parsed_groups_l.append(group)

        return parsed_groups_l

    def __extract_local_accounts(self, computer):
        localAccounts = computer['localUserAccounts']
        delete_keys = ['']
        parsed_accounts_l = []
        for localAccount in localAccounts:
            for delete_key in delete_keys:
                if delete_key in localAccount:
                    del localAccount[delete_key]

            parsed_accounts_l.append(localAccount)

        return parsed_accounts_l

    def __extract_storage(self, computer):
        disks = computer['storage']['disks']
        partitions_l = []
        for disk in disks:
            keys = disk.keys()
            keys_l = []
            for key in keys:
                if key != "partitions":
                    keys_l.append(key)
            for partition in disk['partitions']:
                for key in keys_l:
                    partition[key] = disk[key]
                partitions_l.append(partition)
        return partitions_l

    def __build_splunk_meta(self, meta_keys=[]):

        keys = meta_keys.copy()
        computer_meta = {}
        if 'supervised' in keys:
            computer_meta['supervised'] = self.details['general']['supervised']
        if 'managed' in keys:
            computer_meta['managed'] = self.details['general']['remoteManagement']['managed']
        if 'name' in keys:
            computer_meta['name'] = self.details['general']['name']
        if 'serial_number' in keys:
            computer_meta['serial'] = self.details['hardware']['serialNumber']
        if 'udid' in keys:
            computer_meta['udid'] = self.details['udid']
        if 'id' in keys:
            computer_meta['id'] = self.details['id']
        if 'assigned_user' in keys:
            computer_meta['assignedUser'] = self.details['userAndLocation']['username']
        # To Fix
        if 'department' in keys:
            pass
        if 'building' in keys:
            pass
        if 'room' in keys:
            pass

        """
        Splunk Specific values
        """
        # Time
        if 'timeAsReport' in keys:
            pass

        if 'timeAsContact' in keys:
            # Write Splunks Time Values
            pass

        # Source

        # Hostname

        #
        return computer_meta