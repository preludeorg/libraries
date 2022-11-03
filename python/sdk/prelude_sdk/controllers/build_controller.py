import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def list_manifest(self):
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
    def delete_test(self, name):
        res = requests.delete(f'{self.account.hq}/code/{name}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def create_ttp(self, ttp, question):
        data = dict(id=ttp, question=question)
        res = requests.put(f'{self.account.hq}/manifest', json=data, headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def get_ttp(self, ttp):
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
    def put_test(self, name, code, create=False):
        params = dict(code=code, create=int(create))
        res = requests.post(f'{self.account.hq}/code/{name}', json=params, headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_manifest(self):
        res = requests.delete(f'{self.account.hq}/manifest', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.json()

    @verify_credentials
    def delete_compiled_tests(self):
        res = requests.delete(f'{self.account.hq}/code', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.text
