import os
import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, test_id, name, unit, advisory=None):
        """ Create or update a test """
        body = dict(name=name, unit=unit)
        if advisory:
            body['advisory'] = advisory

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
    def upload(self, test_id, file):
        """ Upload a test or attachment """
        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}/{file.name}',
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)
        res = res.json()

        if os.path.getsize(file) > res['max_content_length']:
            raise Exception('File size must be under 1MB')

        res = requests.post(res['url'], data=res['fields'], files={'file': open(file, 'rb')})
        if not res.status_code == 204:
            raise Exception(res.text)
