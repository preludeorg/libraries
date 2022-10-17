import requests

from detect_sdk.models.account import verify_credentials


class DatabaseController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def print_manifest(self):
        res = requests.get(f'{self.account.hq}/manifest', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_ttp(self, ttp):
        res = requests.delete(f'{self.account.hq}/manifest/{ttp}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def add_ttp(self, ttp, name):
        res = requests.put(f'{self.account.hq}/manifest', json=dict(id=ttp, name=name), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def view_ttp(self, ttp):
        res = requests.get(f'{self.account.hq}/manifest/{ttp}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def clone(self, name):
        res = requests.get(f'{self.account.hq}/code/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def upload_dcf(self, name, code):
        res = requests.post(f'{self.account.hq}/code/{name}', json=dict(code=code), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)
