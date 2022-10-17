import requests

from detect_sdk.models.account import verify_credentials


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
        raise Exception(f'Failed to register endpoint (reason:{res.status_code})')

    @verify_credentials
    def describe_activity(self, endpoint_id=None, days=7):
        """ Get a summary of Account activity, or an individual Endpoint """
        params = dict(id=endpoint_id, days=days)
        res = requests.get(f'{self.account.hq}/account/endpoint/activity', headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to get activity (reason:{res.status_code})')

    @verify_credentials
    def activate_ttp(self, ttp, run_code):
        """ Activate a TTP so endpoints will start running it """
        res = requests.post(
            url=f'{self.account.hq}/account/activation/{ttp}',
            headers=self.account.headers,
            json=dict(run_code=run_code)
        )
        if res.status_code != 200:
            raise Exception(f'Failed to activate: {res.text}')

    @verify_credentials
    def deactivate_ttp(self, ttp):
        """ Deactivate a TTP so endpoints will stop running it """
        res = requests.delete(f'{self.account.hq}/account/activation/{ttp}', headers=self.account.headers)
        if res.status_code != 200:
            raise Exception(f'Failed to deactivate: {res.text}')
