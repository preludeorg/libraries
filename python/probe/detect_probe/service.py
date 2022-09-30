import asyncio
import json
import logging
import os
import socket
import threading
from urllib import request

from detect_probe.presto import Probe


class ProbeService:

    def __init__(self, account_id, secret):
        self.log = logging.getLogger('detect')
        self.account_id = account_id
        self.secret = secret
        self.probe = Probe()
        self._probe_thread = None

    def start(self, token: str):
        """ Start a probe in a separate thread """
        def the_upside_down():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.probe.loop())

        try:
            if not token:
                raise NotImplementedError('Probe requires token to start')
            os.environ['PRELUDE_TOKEN'] = token
            self._probe_thread = threading.Thread(target=the_upside_down, daemon=True)
            self._probe_thread.start()
        except NotImplementedError as ex:
            self.log.warning(ex)

    def stop(self):
        """ Stop a running probe """
        try:
            self._probe_thread.alive = False
        except Exception as ex:
            self.log.error(f'Probe start failure: {ex}')

    def register(self, name=socket.gethostname()) -> str:
        """ Register this endpoint with Detect and return a token """
        try:
            if self.account_id and self.secret:
                r = request.Request(
                    url=f"{os.getenv('PRELUDE_HQ', 'https://detect.prelude.org')}/account/endpoint",
                    data=str.encode(json.dumps(dict(id=name))),
                    headers={
                        'account': self.account_id,
                        'token': self.secret,
                        'Content-Type': 'application/json'
                    })
                with request.urlopen(r) as rs:
                    return rs.read().decode('utf8')
        except Exception as ex:
            self.log.error(f'Probe registration failure: {ex}')
