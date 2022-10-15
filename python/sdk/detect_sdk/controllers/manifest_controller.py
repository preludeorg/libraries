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
        if not res.status_code == 200:
            raise Exception(f'Failed to delete TTP (reason:{res.status_code})')

    @verify_credentials
    def add_ttp(self, ttp, name):
        res = requests.put(f'{self.account.hq}/manifest', json=dict(id=ttp, name=name), headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to add TTP (reason:{res.status_code})')

    @verify_credentials
    def view_ttp(self, ttp):
        res = requests.get(f'{self.account.hq}/manifest/{ttp}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(f'Failed to view TTP (reason:{res.status_code})')

    @verify_credentials
    def clone_dcf(self, name):
        res = requests.get(f'{self.account.hq}/dcf/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.content
        raise Exception(f'Failed to clone DCF (reason:{res.status_code})')

    @verify_credentials
    def delete_dcf(self, name):
        res = requests.delete(f'{self.account.hq}/dcf/{name}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(f'Failed to delete DCF (reason:{res.status_code})')

    @verify_credentials
    def upload_dcf(self, name, code):
        res = requests.post(f'{self.account.hq}/dcf/{name}', json=dict(code=code), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(f'Failed to delete DCF (reason:{res.status_code})')
