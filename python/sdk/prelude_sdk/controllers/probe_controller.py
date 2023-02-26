import requests

from prelude_sdk.spinner import Spinner


class ProbeController:

    def __init__(self, account):
        self.account = account

    def download(self, name: str, dos: str):
        """ Download a probe executable """
        with Spinner():
            res = requests.get(f'{self.account.hq}/download/{name}', headers=dict(dos=dos))
            if not res.status_code == 200:
                raise Exception(res.text)
            return res.text
