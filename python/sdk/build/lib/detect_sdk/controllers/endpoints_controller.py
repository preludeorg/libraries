import requests

from detect_sdk.models.account import verify_credentials


class EndpointsController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def register_endpoint(self, name, tag):
        """ Register (or re-register) an endpoint to your account """
        res = requests.post('%s/account/endpoint' % self.account.hq, headers=self.account.headers, json=dict(id=name, tag=tag if tag else ''))
        if res.status_code == 200:
            return res.text
        raise Exception('Failed to register endpoint: %s' % res.text)

    @verify_credentials
    def describe_activity(self, endpoint_id=None, days=7):
        """ Get a summary of Account activity, or an individual Endpoint """
        params = dict(id=endpoint_id, days=days)
        res = requests.get('%s/account/endpoint/activity' % self.account.hq, headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to get activity: %s' % res.text)
