""" This Class is used to pull in Device Check Points """
import json
import os
import time


class CheckPoint:

    def __init__(self):
        self.working_dir = "app/device_checkpoint/"
        pass

    def get_computer(self, jss_id):
        """
        Get a computer from teh Checkpoint system based on the JSS_ID
        :param jss_id: the JSS_ID in INT or STR
        :return: Computer_META : Dict, Computer_Detail: Dict
        """
        with open(f'{self.working_dir}files/meta.json', "r") as fp:
            computer_meta = json.loads(fp.read())
        response_meta = {}
        for computer in computer_meta['computers']:
            if computer['id'] == str(jss_id):
                response_meta = computer
        try:
            with open(f'{self.working_dir}files/computerDetails/computer_{jss_id}.json', 'r') as fp:
                response_details = json.loads(fp.read())
        except IOError:
            response_details = {}

        if response_meta == {}:
            return None, None

        if response_details == {}:
            return response_meta, None

        return computer_meta, response_details

    def write_computer(self, jss_id, computer_meta={}, computer_details={}):
        """
        This function will update the Computer to the Checkpoint
        :param jss_id: INT or STR of JamfPro ID
        :param computer_meta: ComputerSlice from HEC DICT
        :param computer_details: Full computer from UAPI
        :return: Bool on if successful
        """
        try:
            with open(f"{self.working_dir}files/computerDetails/computer_{jss_id}.json", "w+") as fp:
                fp.write(json.dumps(computer_details, indent=2))
        except IOError:
            return False


        with open(f"{self.working_dir}files/meta.json", "r") as fp:

            meta =json.loads(fp.read())
            new_computer_l = []
            updated_computer = False
            for computer in meta['computers']:
                if computer['id'] == computer_meta['id']:
                    new_computer_l.append(computer_meta)
                    updated_computer = True
                else:
                    new_computer_l.append(computer)
            if not updated_computer:
                new_computer_l.append(computer_meta)

            meta['computers'] = new_computer_l
        with open(f"{self.working_dir}files/meta.json", "w+") as fp:
            fp.write(json.dumps(meta, indent=2))


        return True