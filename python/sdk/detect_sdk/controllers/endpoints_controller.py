import requests

from detect_sdk.models.account import verify_credentials


class EndpointsController:

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
