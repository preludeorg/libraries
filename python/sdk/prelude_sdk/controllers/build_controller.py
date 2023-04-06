import requests

from prelude_sdk.spinner import Spinner
from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, test_id, name):
        """ Create or update a test """
        with Spinner():
            res = requests.post(
                f'{self.account.hq}/build/tests/{test_id}', 
                json=dict(name=name),
                headers=self.account.headers,
                timeout=10
            )
            if not res.status_code == 200:
                raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        """ Delete an existing test """
        with Spinner():
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
        with Spinner():
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
        with Spinner():
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
        with Spinner():
            res = requests.post(
                f'{self.account.hq}/build/tests/{test_id}/{filename}',
                data=data,
                headers=h,
                timeout=10
            )
            if not res.status_code == 200:
                raise Exception(res.text)

    @verify_credentials
    def map(self, test_id: str, x: str):
        """ Add a classification property to a test """
        with Spinner():
            res = requests.post(
                f'{self.account.hq}/build/tests/{test_id}/map/{x}', 
                json=dict(id=test_id),
                headers=self.account.headers,
                timeout=10
            )
            if not res.status_code == 200:
                raise Exception(res.text)

    @verify_credentials
    def unmap(self, test_id: str, x: str):
        """ Remove a classification property from a test """
        with Spinner():
            res = requests.delete(
                f'{self.account.hq}/build/tests/{test_id}/map/{x}', 
                json=dict(id=test_id),
                headers=self.account.headers,
                timeout=10
            )
            if not res.status_code == 200:
                raise Exception(res.text)
