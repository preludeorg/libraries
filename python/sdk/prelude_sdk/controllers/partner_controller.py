import requests

from prelude_sdk.controllers.http_controller import HttpController

from prelude_sdk.models.codes import Control
from prelude_sdk.models.account import verify_credentials


class PartnerController(HttpController):

    def __init__(self, account):
        super().__init__()
        self.account = account

    @verify_credentials
    def attach(self, partner: Control, api: str, user: str, secret: str):
        """ Attach a partner to your account """
        params = dict(api=api, user=user, secret=secret)
        res = self._session.post(
            f'{self.account.hq}/partner/{partner.name}',
            headers=self.account.headers,
            json=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def detach(self, partner: Control):
        """ Detach a partner from your Detect account """
        res = self._session.delete(
            f'{self.account.hq}/partner/{partner.name}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def block(self, partner: Control, test_id: str):
        """ Report to a partner to block a test """
        params = dict(test_id=test_id)
        res = self._session.post(
            f'{self.account.hq}/partner/block/{partner.name}',
            headers=self.account.headers,
            json=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
        
    @verify_credentials
    def endpoints(self, partner: Control, platform: str, hostname: str = '', offset: int = 0, count: int = 100):
        """ Get a list of endpoints from a partner """
        params = dict(platform=platform, hostname=hostname, offset=offset, count=count)
        res = self._session.get(
            f'{self.account.hq}/partner/endpoints/{partner.name}',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def generate_webhook(self, partner: Control):
        """ Generate webhook credentials for an EDR system to enable the forwarding of alerts to the Prelude API, facilitating automatic alert suppression """
        res = self._session.get(
            f'{self.account.hq}/partner/suppress/{partner.name}',
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def deploy(self, partner: Control, host_ids: list):
        """ Deploy probes on all specified partner endpoints """
        params = dict(host_ids=host_ids)
        res = self._session.post(
            f'{self.account.hq}/partner/deploy/{partner.name}',
            headers=self.account.headers,
            json=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_reports(self, partner: Control, test_id: str):
        """ Get reports to a partner for a test """
        params = dict(test_id=test_id)
        res = self._session.get(
            f'{self.account.hq}/partner/reports/{partner.name}',
            headers=self.account.headers,
            json=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
