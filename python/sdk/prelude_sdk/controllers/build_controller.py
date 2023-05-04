import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, test_id, name, unit, alert=None):
        """ Create or update a test """
        body = dict(name=name, unit=unit)
        if alert is not None:
            body['alert'] = alert
        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        """ Delete an existing test """
        res = requests.delete(
            f'{self.account.hq}/build/tests/{test_id}',
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def get_test(self, test_id):
        """ Get properties of an existing test """
        res = requests.get(
            f'{self.account.hq}/build/tests/{test_id}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def download(self, test_id, filename):
        """ Clone a test file or attachment"""
        res = requests.get(
            f'{self.account.hq}/build/tests/{test_id}/{filename}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def upload(self, test_id, filename, data, binary=False):
        """ Upload a test or attachment """
        h = self.account.headers | ({'Content-Type': 'application/octet-stream'} if binary else {})
        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}/{filename}',
            data=data,
            headers=h,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)
