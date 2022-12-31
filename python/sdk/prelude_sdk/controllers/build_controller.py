import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def list_tests(self):
        res = requests.get(f'{self.account.hq}/build/tests', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_test(self, test_id, truth):
        data = dict(id=test_id, truth=truth)
        res = requests.post(f'{self.account.hq}/build/tests', json=data, headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        res = requests.delete(f'{self.account.hq}/build/tests/{test_id}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def download_test(self, name):
        res = requests.get(f'{self.account.hq}/build/source/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def upload_test(self, name, code):
        res = requests.post(f'{self.account.hq}/build/source/{name}', json=dict(code=code), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def create_url(self, vst: str):
        res = requests.get(f'{self.account.hq}/build/{vst}/url', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def compute(self, name: str):
        res = requests.post(f'{self.account.hq}/build/compute', json=dict(name=name), headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
