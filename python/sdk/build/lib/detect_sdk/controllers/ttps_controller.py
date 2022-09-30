import requests

from detect_sdk.models.account import verify_credentials


class TTPsController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def list_ttps(self):
        res = requests.get('%s/manifest' % self.account.hq, headers=self.account.headers)
        if res.status_code == 200:
            return res.json()
        raise Exception('Failed to retrieve manifest (reason:%s' % res.status_code)

    @verify_credentials
    def activate_ttp(self, ttp, run_code):
        """ Activate a TTP so endpoints will start running it """
        res = requests.post(
            url='%s/account/activation/%s' % (self.account.hq, ttp),
            headers=self.account.headers,
            json=dict(run_code=run_code)
        )
        if res.status_code != 200:
            raise Exception('Failed to activate: %s' % res.text)

    @verify_credentials
    def deactivate_ttp(self, ttp):
        """ Deactivate a TTP so endpoints will stop running it """
        res = requests.delete('%s/account/activation/%s' % (self.account.hq, ttp), headers=self.account.headers)
        if res.status_code != 200:
            raise Exception('Failed to deactivate: %s' % res.text)
