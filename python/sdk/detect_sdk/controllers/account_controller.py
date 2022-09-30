import requests

from detect_sdk.models.account import verify_credentials


class AccountController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_user(self, permission, label):
        res = requests.post(
            url='%s/account/user' % self.account.hq,
            json=dict(permission=permission, label=label),
            headers=self.account.headers
        )
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to create user (reason:%s)' % res.status_code)

    @verify_credentials
    def delete_user(self, token):
        res = requests.delete('%s/account/user' % self.account.hq, json=dict(token=token), headers=self.account.headers)
        if res.status_code == 200:
            return True
        raise Exception('Failed to delete user (reason:%s)' % res.status_code)

    @verify_credentials
    def describe_account(self):
        res = requests.get('%s/account' % self.account.hq, headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to get Account (reason:%s)' % res.status_code)

    @verify_credentials
    def update_token(self, token):
        """ Update Account token """
        res = requests.put('%s/account' % self.account.hq, headers=self.account.headers, json=dict(token=token))
        if res.status_code != 200:
            raise Exception('Failed to update token: %s' % res.text)
        cfg = self.account.read_keychain_config()
        cfg[self.account.profile]['token'] = token
        self.account.write_keychain_config(cfg)

    @verify_credentials
    def describe_activity(self, days=7):
        """ Get a summary of Account activity """
        params = dict(days=days)
        res = requests.get('%s/account/activity' % self.account.hq, headers=self.account.headers, params=params)
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to get activity: %s' % res.text)
