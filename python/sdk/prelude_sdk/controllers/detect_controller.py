import requests

from prelude_sdk.models.account import verify_credentials


class DetectController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def register_endpoint(self, host, serial_num, tags=None):
        """ Register (or re-register) an endpoint to your account """
        body = dict(id=f'{host}:{serial_num}')
        if tags:
            body['tags'] = tags

        res = requests.post(
            f'{self.account.hq}/detect/endpoint',
            headers=self.account.headers,
            json=body,
            timeout=10
        )
        if res.status_code == 200:
            return res.text
        raise Exception(res.text)

    @verify_credentials
    def update_endpoint(self, endpoint_id, tags=None):
        """ Update an endpoint in your account """
        body = dict()
        if tags is not None:
            body['tags'] = tags

        res = requests.post(
            f'{self.account.hq}/detect/endpoint/{endpoint_id}',
            headers=self.account.headers,
            json=body,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_endpoint(self, ident: str):
        """ Delete an endpoint from your account """
        params = dict(id=ident)
        res = requests.delete(
            f'{self.account.hq}/detect/endpoint',
            headers=self.account.headers,
            json=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_endpoints(self, days: int = 90):
        """ List all endpoints on your account """
        params = dict(days=days)
        res = requests.get(
            f'{self.account.hq}/detect/endpoint',
            headers=self.account.headers,
            params=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_advisories(self, year: int = None):
        """ List advisories """
        params = dict(year=year) if year else {}
        res = requests.get(
            f'{self.account.hq}/detect/advisories',
            headers=self.account.headers,
            params=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def describe_activity(self, filters: dict, view: str = 'default'):
        """ Get report for an Account """
        params = dict(view=view, **filters)
        res = requests.get(
            f'{self.account.hq}/detect/activity',
            headers=self.account.headers,
            params=params,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_tests(self):
        """ List all tests available to an account """
        res = requests.get(
            f'{self.account.hq}/detect/tests',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def get_test(self, test_id):
        """ Get properties of an existing test """
        res = requests.get(
            f'{self.account.hq}/detect/tests/{test_id}',
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
            f'{self.account.hq}/detect/tests/{test_id}/{filename}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.content
        raise Exception(res.text)

    @verify_credentials
    def enable_test(self, ident: str, run_code: int, tags: str):
        """ Enable a test so endpoints will start running it """
        res = requests.post(
            url=f'{self.account.hq}/detect/queue/{ident}',
            headers=self.account.headers,
            json=dict(code=run_code, tags=tags),
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def disable_test(self, ident: str, tags: str):
        """ Disable a test so endpoints will stop running it """
        res = requests.delete(
            f'{self.account.hq}/detect/queue/{ident}',
            headers=self.account.headers,
            params=dict(tags=tags),
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
