import requests
import datetime

from prelude_sdk.models.account import verify_credentials


class IAMController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def new_account(self, user_email: str, user_name: str):
        res = requests.post(
            url=f'{self.account.hq}/iam/account',
            json=dict(handle=user_email, user_name=user_name),
            headers=self.account.headers,
            timeout=10
        )
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
        """ Delete an account and all things in it """
        res = requests.delete(
            f'{self.account.hq}/iam/account',
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.text

    @verify_credentials
    def update_account(self, mode: int):
        """ Update properties on an account """
        res = requests.put(
            f'{self.account.hq}/iam/account',
            headers=self.account.headers,
            json=dict(mode=mode),
            timeout=10
        )
        if res.status_code != 200:
            raise Exception(res.text)

    @verify_credentials
    def get_account(self):
        """ Get account properties """
        res = requests.get(
            f'{self.account.hq}/iam/account',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_user(self, permission: int, email: str, name: str, expires: datetime):
        """ Create a new user inside an account """
        res = requests.post(
            url=f'{self.account.hq}/iam/user',
            json=dict(permission=permission, handle=email, name=name, expires=expires.isoformat()),
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_user(self, handle):
        """ Delete a user from an account """
        res = requests.delete(
            f'{self.account.hq}/iam/user',
            json=dict(handle=handle),
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return True
        raise Exception(res.text)

    @verify_credentials
    def audit_logs(self, days: int = 7, limit: int = 1000):
        """ Get audit logs from the last X days """
        params = dict(days=days, limit=limit)
        res = requests.get(
            f'{self.account.hq}/iam/audit',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
