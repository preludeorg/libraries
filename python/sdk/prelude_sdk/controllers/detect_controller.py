import requests

from prelude_sdk.spinner import Spinner
from prelude_sdk.models.account import verify_credentials


class DetectController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def register_endpoint(self, host, serial_num, edr_id, tags):
        """ Register (or re-register) an endpoint to your account """
        with Spinner():
            params = dict(id=f'{host}:{serial_num}:{edr_id}', tags=tags)
            res = requests.post(
                f'{self.account.hq}/detect/endpoint',
                headers=self.account.headers,
                json=params,
                timeout=10
            )
            if res.status_code == 200:
                return res.text
            raise Exception(res.text)

    @verify_credentials
    def delete_endpoint(self, ident: str):
        """ Delete an endpoint from your account """
        with Spinner():
            params = dict(id=ident)
            res = requests.delete(
                f'{self.account.hq}/detect/endpoint',
                headers=self.account.headers,
                json=params,
                timeout=10
            )
            if res.status_code != 200:
                raise Exception(res.text)

    @verify_credentials
    def list_endpoints(self, days: int = 90):
        """ List all endpoints on your account """
        with Spinner():
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
    def describe_activity(self, filters: dict, view: str = 'logs'):
        """ Get report for an Account """
        with Spinner():
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
    def list_queue(self):
        """ List all tests in the queue """
        with Spinner():
            res = requests.get(
                f'{self.account.hq}/detect/queue',
                headers=self.account.headers,
                timeout=10
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def list_tests(self):
        """ List all tests available to an account """
        with Spinner():
            res = requests.get(
                f'{self.account.hq}/detect/tests',
                headers=self.account.headers,
                timeout=10
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def enable_test(self, ident: str, run_code: int, tags: str):
        """ Enable a test so endpoints will start running it """
        with Spinner():
            res = requests.post(
                url=f'{self.account.hq}/detect/queue/{ident}',
                headers=self.account.headers,
                json=dict(code=run_code, tags=tags),
                timeout=10
            )
            if res.status_code != 200:
                raise Exception(res.text)

    @verify_credentials
    def disable_test(self, ident):
        """ Disable a test so endpoints will stop running it """
        with Spinner():
            res = requests.delete(
                f'{self.account.hq}/detect/queue/{ident}',
                headers=self.account.headers,
                timeout=10
            )
            if res.status_code != 200:
                raise Exception(res.text)

    @verify_credentials
    def social_stats(self, ident: str, days: int = 30):
        """ Pull social statistics for a specific test """
        with Spinner():
            res = requests.get(
                f'{self.account.hq}/detect/{ident}/social',
                headers=self.account.headers,
                params=dict(days=days),
                timeout=10
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def search(self, identifier: str):
        """ Search the NVD for a keyword """
        with Spinner():
            res = requests.get(
                f'{self.account.hq}/detect/search',
                headers=self.account.headers,
                params=dict(identifier=identifier),
                timeout=10
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def recommendations(self):
        """ List all security recommendations for your account """
        with Spinner():
            res = requests.get(
                f'{self.account.hq}/detect/recommendations',
                headers=self.account.headers,
                timeout=10
            )
            if res.status_code == 200:
                return res.json()
            raise Exception(res.text)

    @verify_credentials
    def create_recommendation(self, title: str, description: str):
        """ Create a new security recommendation """
        with Spinner():
            params = dict(title=title, description=description)
            res = requests.post(
                f'{self.account.hq}/detect/recommendations',
                headers=self.account.headers,
                json=params,
                timeout=10
            )
            if res.status_code != 200:
                raise Exception(res.text)

    @verify_credentials
    def make_decision(self, id: str, decision: int):
        """ Add a new decision for a security recommendation """
        with Spinner():
            params = dict(decision=decision)
            res = requests.post(
                f'{self.account.hq}/detect/recommendations/{id}',
                headers=self.account.headers,
                json=params,
                timeout=10
            )
            if res.status_code != 200:
                raise Exception(res.text)
