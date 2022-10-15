import requests

from detect_sdk.models.account import verify_credentials


class ManifestController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def print_manifest(self):
        res = requests.get(f'{self.account.hq}/manifest', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to print manifest (reason:{res.status_code})')

    @verify_credentials
    def delete_ttp(self, ttp):
        res = requests.delete(f'{self.account.hq}/manifest/{ttp}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to delete TTP (reason:{res.status_code})')

    @verify_credentials
    def add_ttp(self, ttp, name):
        res = requests.post(f'{self.account.hq}/manifest/{ttp}', json=dict(name=name), headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to delete TTP (reason:{res.status_code})')
