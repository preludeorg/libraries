import requests
import datetime

from prelude_sdk.spinner import Spinner
from prelude_sdk.models.account import verify_credentials


class IAMController:

    def __init__(self, account, plaintext):
        self.account = account
        self.plaintext = plaintext

    @verify_credentials
    def new_account(self, handle):
        with Spinner(self.plaintext):
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
        """ Delete an account and all things in it """
        with Spinner(self.plaintext):
            res = requests.delete(f'{self.account.hq}/iam/account', headers=self.account.headers)
            if not res.status_code == 200:
                raise Exception(res.text)
            return res.text

    @verify_credentials
    def get_account(self):
        """ Get account properties """
        with Spinner(self.plaintext):
            res = requests.get(f'{self.account.hq}/iam/account', headers=self.account.headers)
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def create_user(self, permission: int, handle: str, expires: datetime):
        """ Create a new user inside an account """
        with Spinner(self.plaintext):
            res = requests.post(
                url=f'{self.account.hq}/iam/user',
                json=dict(permission=permission, handle=handle, expires=expires.isoformat()),
                headers=self.account.headers
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def delete_user(self, handle):
        """ Delete a user from an account """
        with Spinner(self.plaintext):
            res = requests.delete(f'{self.account.hq}/iam/user', json=dict(handle=handle), headers=self.account.headers)
            if res.status_code == 200:
                return True
            raise Exception(res.text)

    @verify_credentials
    def attach_control(self, name: str, api: str, user: str, secret: str = ''):
        """ Attach a control to your Detect account """
        with Spinner(self.plaintext):
            params = dict(name=name, api=api, user=user, secret=secret)
            res = requests.post(f'{self.account.hq}/iam/control', headers=self.account.headers, json=params)
            if res.status_code == 200:
                return res.text
            raise Exception(res.text)

    @verify_credentials
    def detach_control(self, name: str):
        """ Detach a control from your Detect account """
        with Spinner(self.plaintext):
            params = dict(name=name)
            res = requests.delete(f'{self.account.hq}/iam/control', headers=self.account.headers, json=params)
            if res.status_code == 200:
                return res.text
            raise Exception(res.text)
