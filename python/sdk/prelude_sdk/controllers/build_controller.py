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
    def create_test(self, test_id, name):
        data = dict(name=name)
        res = requests.post(f'{self.account.hq}/build/tests/{test_id}', json=data, headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        res = requests.delete(f'{self.account.hq}/build/tests/{test_id}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def get_test(self, test_id):
        res = requests.get(f'{self.account.hq}/build/tests/{test_id}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def download(self, test_id, filename):
        res = requests.get(f'{self.account.hq}/build/tests/{test_id}/{filename}', headers=self.account.headers)
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def upload(self, test_id, filename, code):
        res = requests.post(f'{self.account.hq}/build/tests/{test_id}/{filename}', json=dict(code=code), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def create_url(self, attachment: str):
        res = requests.get(f'{self.account.hq}/build/{attachment}/url', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def compute(self, test_id: str):
        res = requests.post(f'{self.account.hq}/build/compute', json=dict(id=test_id), headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
