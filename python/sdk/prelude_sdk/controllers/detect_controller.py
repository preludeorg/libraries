import requests

from prelude_sdk.models.account import verify_credentials


class DetectController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def register_endpoint(self, name, tag=''):
        """ Register (or re-register) an endpoint to your account """
        params = dict(id=name, tag=tag)
        res = requests.post(f'{self.account.hq}/account/endpoint', headers=self.account.headers, json=params)
        if res.status_code == 200:
            return res.text
        raise Exception(res.text)

    @verify_credentials
    def endpoint_activity(self, endpoint_id, days=7):
        """ Get results for an individual Endpoint """
        params = dict(id=endpoint_id, days=days)
        res = requests.get(f'{self.account.hq}/account/endpoint/activity', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def account_activity(self, days=7):
        """ Get report for an Account """
        params = dict(days=days)
        res = requests.get(f'{self.account.hq}/account/activity', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def print_queue(self):
        res = requests.get(f'{self.account.hq}/account/queue', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def activate_ttp(self, ttp, run_code):
        """ Activate a TTP so endpoints will start running it """
        res = requests.post(
            url=f'{self.account.hq}/account/activation/{ttp}',
            headers=self.account.headers,
            json=dict(run_code=run_code)
        )
        if res.status_code != 200:
            raise Exception(res.text)

    @verify_credentials
    def deactivate_ttp(self, ttp):
        """ Deactivate a TTP so endpoints will stop running it """
        res = requests.delete(f'{self.account.hq}/account/activation/{ttp}', headers=self.account.headers)
        if res.status_code != 200:
            raise Exception(res.text)
