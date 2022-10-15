import requests

from detect_sdk.models.account import verify_credentials


class OperatorController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def print_manifest(self):
        res = requests.get('%s/manifest' % self.account.hq, headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to retrieve manifest (reason:%s' % res.status_code)
