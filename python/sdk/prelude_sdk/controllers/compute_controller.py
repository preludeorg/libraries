import requests

from prelude_sdk.models.account import verify_credentials


class ComputeController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def describe_server(self):
        res = requests.get(f'{self.account.hq}/compute', headers=self.account.headers)
        if res.status_code == 200:
            return res.text
        raise Exception(res.text)

    @verify_credentials
    def create_url(self, name):
        res = requests.get(f'{self.account.hq}/compute/deploy/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
