"""
This is a Splunk Class that assists in writing to an HEC connector
"""
import asyncio
import json
import requests
import aiohttp



# ToDo: Add the ability to set the fields: TIME, HOST, SOURCE, SOURCETYPE, and INDEX ( https://docs.splunk.com/Documentation/SplunkCloud/latest/Data/FormateventsforHTTPEventCollector )
# ToDo: Convert to Package with __INIT__.py
# ToDo: Finish writing Batch
class SplunkTools:
    """
    This is a class that assists in writing to the HEC connector
    """
    events = []

    def __chunks(self, batch_size=100):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(self.events), batch_size):
            yield self.events[i:i + batch_size]

    def __init__(self, host, splunk_token):
        """
        INIT
        :param host: "HTTPS://<YourSplunkServer.Domain/Endpoint>
        :param splunk_token: HEC Token
        """

        self.headers = {"Authorization": f"Splunk {splunk_token}", 'Content-Type': 'application/json'}
        self.url = host

    def post_to_splunk(self, splunk_log: str):
        """
        post a single Event to Splunk, Log is STR
        :param splunk_log: STR that is JSON serializable
        :return: True if Completed
        """
        DATA = {
            "event": splunk_log,
            "sourcetype": "_json"
        }
        response = requests.post(self.url, data=json.dumps(DATA), headers=self.headers)
        if response.status_code == 200:
            return True
        return False

    def post_async_to_splunk(self, splunk_logs: list) -> None:
        """
        Async Method of writing to Splunk JSON objects
        :param splunk_logs: Array of Splunk Logs
        :return: None
        """
        asyncio.run(self.__async_posts(splunk_logs=splunk_logs))

    async def __async_posts(self, splunk_logs: list) -> None:
        """
        Private function that writes the individual logs directly to splunk
        :param splunk_logs:
        :return: None
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            for splunk_log in splunk_logs:
                DATA = {
                    "event": splunk_log,
                    "sourcetype": "_json"
                }

                async with session.post(url=self.url, data=json.dumps(DATA), headers=self.headers) as resp:
                    await resp.json()

    def add_event(self, event: dict):
        """
        This funciton will add an event to the array of events
        :param event: The _json dictionary of the event
        :return: None
        """
        event_details = {}
        keys = ['time', 'source', 'host', 'sourcetype']

        for key in keys:
            if key in event:
                event_details[key] = event[key]
                del event[key]

        event_details['event'] = event

        self.events.append(event_details)

    def __write_batched_event(self, events) -> bool:
        """
        Writes a single batch of events
        :param events: Array of Events
        :return:
        """
        response = requests.post(self.url, data=json.dumps(events), headers=self.headers)
        if response.status_code == 200:
            return True

        return False

    async def __write_batched_event_async(self, events) -> bool:
        """
        Writes a single batch of events
        :param events: Array of Events
        :return:
        """

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            for splunk_log in events:

                async with session.post(url=self.url, data=json.dumps(splunk_log), headers=self.headers) as resp:
                    await resp.json()

    async def __async_posts_batch(self, splunk_logs: list) -> None:
        """
        Private function that writes the individual logs directly to splunk
        :param splunk_logs:
        :return: None
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            for splunk_log in splunk_logs:


                async with session.post(url=self.url, data=json.dumps(splunk_log), headers=self.headers) as resp:
                    await resp.json()
                    print(resp.status)


    def write_batch_events(self, batch_size=100, sync=True) -> bool:
        """
        Writes the list of batch events in groups of the batch size. Careful about using A large Batch size AND Async
        :param batch_size: INT Default =100. The amount of events to write in one group
        :param sync: True, write sequentially, False: use Async method
        :return:
        """
        events_l = self.get_events(chunk=batch_size)
        if sync:
            for events in events_l:
                self.__write_batched_event(events=events)
        else:
            asyncio.run(self.__write_batched_event_async(events= events_l))
        self.events = []

        return True

    def get_events(self, chunk=0):
        """
        returns the currently list of events
        :return: List of event Dictionaries
        """
        if chunk == 0:
            return self.events

        chunked = list(self.__chunks(batch_size=chunk))
        return chunked
