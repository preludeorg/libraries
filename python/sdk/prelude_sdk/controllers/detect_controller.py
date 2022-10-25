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

    @verify_credentials
    def describe_activity(self, days=7, ttp=None):
        """ Get report for an Account """
        params = dict(days=days)
        route = f'/{ttp}' if ttp else ''
        res = requests.get(f'{self.account.hq}/account/report{route}', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def export_report(self, days=7):
        """ Generate a redirect URL to a data dump """
        params = dict(days=days)
        res = requests.get(f'{self.account.hq}/account/report-export', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.url
        raise Exception(res.text)
