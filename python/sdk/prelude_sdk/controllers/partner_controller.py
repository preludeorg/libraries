import requests

from prelude_sdk.spinner import Spinner
from prelude_sdk.models.account import verify_credentials


class PartnerController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def endpoints(self, partner_name: str, platform: str, hostname: str = '', offset: int = 0):
        """ Get a list of endpoints from all partners """
        with Spinner():
            params = dict(platform=platform, hostname=hostname, offset=offset)
            res = requests.get(
                f'{self.account.hq}/partner/{partner_name}',
                headers=self.account.headers,
                params=params,
                timeout=30
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def deploy(self, partner_name: str, host_ids: list):
        """ Deploy probes on all specified partner endpoints """
        with Spinner():
            params = dict(host_ids=host_ids)
            res = requests.post(
                f'{self.account.hq}/partner/{partner_name}',
                headers=self.account.headers,
                json=params,
                timeout=30
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)
