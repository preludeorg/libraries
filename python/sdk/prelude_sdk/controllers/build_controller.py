import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, name, unit, techniques=None, advisory=None, test_id=None):
        """ Create or update a test """
        body = dict(name=name, unit=unit)
        if techniques:
            body['techniques'] = techniques
        if advisory:
            body['advisory'] = advisory
        if test_id:
            body['id'] = test_id

        res = requests.post(
            f'{self.account.hq}/build/tests',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_test(self, test_id, name=None, unit=None, techniques=None, advisory=None):
        """ Update a test """
        body = dict()
        if name:
            body['name'] = name
        if unit:
            body['unit'] = unit
        if techniques is not None:
            body['techniques'] = techniques
        if advisory is not None:
            body['advisory'] = advisory

        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        """ Delete an existing test """
        res = requests.delete(
            f'{self.account.hq}/build/tests/{test_id}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def upload(self, test_id, filename, data):
        """ Upload a test or attachment """
        if len(data) > 1000000:
            raise ValueError(f'File size must be under 1MB ({filename})')

        h = self.account.headers | {'Content-Type': 'application/octet-stream'}
        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}/{filename}',
            data=data,
            headers=h,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
