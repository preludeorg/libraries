import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def list_tests(self):
        res = requests.get(f'{self.account.hq}/test', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_test(self, ident):
        res = requests.delete(f'{self.account.hq}/test/{ident}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_variant(self, name):
        res = requests.delete(f'{self.account.hq}/variant/{name}', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def create_test(self, ident, question):
        data = dict(id=ident, question=question)
        res = requests.put(f'{self.account.hq}/test', json=data, headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def get_test(self, ident):
        res = requests.get(f'{self.account.hq}/test/{ident}', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def clone(self, name):
        res = requests.get(f'{self.account.hq}/variant/{name}', headers=self.account.headers)
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def create_variant(self, name, code):
        res = requests.post(f'{self.account.hq}/variant/{name}', json=dict(code=code), headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def purge_account(self):
        res = requests.delete(f'{self.account.hq}/account/purge', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.text
