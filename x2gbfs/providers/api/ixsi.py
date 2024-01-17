import asyncio
from datetime import datetime, timezone

from websockets.sync.client import connect


class IxsiAPI:
    def __init__(self, system_id: str, uri: str, timeout=5, max_size=2**24):
        """
        Send a message to a recipient.

        :param str system_id: ID of the requesting system, assigned by cantamen
        :param str uri: uri of the IXSI v5 service, e.g. wss://service.my.org/ixsi/v5
        :param int timeout: request timeout
        """
        self.system_id = system_id
        self.uri = uri
        self.timeout = timeout
        self.max_size = max_size

    def _request(self, message):
        with connect(self.uri, max_size=self.max_size) as websocket:
            websocket.send(message)
            return websocket.recv(timeout=self.timeout)

    def result_for_provider(self, provider_id: int):
        timestamp = datetime.fromtimestamp(datetime.now().timestamp(), tz=timezone.utc).isoformat()
        message = '''<?xml version="1.0" encoding="UTF-8"?><Ixsi xmlns="http://www.ixsi-schnittstelle.de/">
                <Request>
                        <Transaction>
                                <TimeStamp>{}</TimeStamp>
                                <MessageID>{}</MessageID>
                        </Transaction>
                        <SystemID>{}</SystemID>
                        <BaseData>
                                <ProviderFilter>{}</ProviderFilter>
                                <IncludeBookees>true</IncludeBookees>
                                <IncludeChargers>true</IncludeChargers>
                        </BaseData>
                </Request>
        </Ixsi>
        '''.format(
            timestamp, 1, self.system_id, provider_id
        )
        return self._request(message)
