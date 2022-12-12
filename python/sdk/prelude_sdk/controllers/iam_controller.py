import requests

from prelude_sdk.models.account import verify_credentials


class IAMController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def new_account(self, handle):
        res = requests.post(url=f'{self.account.hq}/iam/account', json=dict(handle=handle), headers=self.account.headers)
        if res.status_code != 200:
            raise Exception(res.text)
        cfg = self.account.read_keychain_config()
        res_json = res.json()
        cfg[self.account.profile]['account'] = res_json['account_id']
        cfg[self.account.profile]['token'] = res_json['token']
        self.account.write_keychain_config(cfg)
        return res_json

    @verify_credentials
    def purge_account(self):
        res = requests.delete(f'{self.account.hq}/iam/account', headers=self.account.headers)
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.text

    @verify_credentials
    def get_users(self):
        res = requests.get(f'{self.account.hq}/iam/user', headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_user(self, permission, handle):
        res = requests.post(
            url=f'{self.account.hq}/iam/user',
            json=dict(permission=permission, handle=handle),
            headers=self.account.headers
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_user(self, handle):
        res = requests.delete(f'{self.account.hq}/iam/user', json=dict(handle=handle), headers=self.account.headers)
        if res.status_code == 200:
            return True
        raise Exception(res.text)
