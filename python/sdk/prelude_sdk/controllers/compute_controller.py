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
    def compute_proxy(self, route: str, data: dict):
        res = requests.post(f'{self.account.hq}/compute/proxy/{route}', json=data, headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_url(self, name: str):
        res = requests.get(f'{self.account.hq}/compute/url/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
