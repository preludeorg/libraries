import requests

from prelude_sdk.models.account import verify_credentials


class PartnerController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def attach(self, name: str, api: str, user: str, secret: str):
        """ Attach a partner to your account """
        params = dict(api=api, user=user, secret=secret)
        res = requests.post(
            f'{self.account.hq}/partner/{name}',
            headers=self.account.headers,
            json=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def detach(self, name: str):
        """ Detach a partner from your Detect account """
        res = requests.delete(
            f'{self.account.hq}/partner/{name}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.text
        raise Exception(res.text)
        
    @verify_credentials
    def endpoints(self, partner_name: str, platform: str, hostname: str = '', offset: int = 0, count: int = 100):
        """ Get a list of endpoints from all partners """
        params = dict(platform=platform, hostname=hostname, offset=offset, count=count)
        res = requests.get(
            f'{self.account.hq}/partner/endpoints/{partner_name}',
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
        params = dict(host_ids=host_ids)
        res = requests.post(
            f'{self.account.hq}/partner/deploy/{partner_name}',
            headers=self.account.headers,
            json=params,
            timeout=30
        )
        if not res.status_code == 200:
            raise Exception(res.text)
