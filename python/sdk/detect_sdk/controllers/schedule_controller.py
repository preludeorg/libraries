import requests

from detect_sdk.models.account import verify_credentials


class ScheduleController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def activate_ttp(self, ttp, run_code):
        """ Activate a TTP so endpoints will start running it """
        res = requests.post(
            url=f'{self.account.hq}/account/activation/{ttp}',
            headers=self.account.headers,
            json=dict(run_code=run_code)
        )
        if res.status_code != 200:
            raise Exception(f'Failed to activate: {res.text}')

    @verify_credentials
    def deactivate_ttp(self, ttp):
        """ Deactivate a TTP so endpoints will stop running it """
        res = requests.delete(f'{self.account.hq}/account/activation/{ttp}', headers=self.account.headers)
        if res.status_code != 200:
            raise Exception(f'Failed to deactivate: {res.text}')
