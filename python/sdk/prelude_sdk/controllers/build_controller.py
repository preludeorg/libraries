import requests

from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, name, unit, technique=None, test_id=None):
        """ Create or update a test """
        body = dict(name=name, unit=unit)
        if technique:
            body['technique'] = technique
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
    def update_test(self, test_id, name=None, unit=None, technique=None):
        """ Update a test """
        body = dict()
        if name:
            body['name'] = name
        if unit:
            body['unit'] = unit
        if technique is not None:
            body['technique'] = technique

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
    def delete_test(self, test_id, purge):
        """ Delete an existing test """
        res = requests.delete(
            f'{self.account.hq}/build/tests/{test_id}',
            json=dict(purge=purge),
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

    @verify_credentials
    def create_threat(self, name, published, threat_id=None, source_id=None, source=None, tests=None):
        """ Create a threat """
        body = dict(name=name, published=published)
        if threat_id:
            body['id'] = threat_id
        if source_id:
            body['source_id'] = source_id
        if source:
            body['source'] = source
        if tests:
            body['tests'] = tests

        res = requests.post(
            f'{self.account.hq}/build/threats',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_threat(self, threat_id, name=None, source_id=None, source=None, published=None, tests=None):
        """ Update a threat """
        body = dict()
        if name:
            body['name'] = name
        if source_id is not None:
            body['source_id'] = source_id
        if source is not None:
            body['source'] = source
        if published is not None:
            body['published'] = published
        if tests is not None:
            body['tests'] = tests

        res = requests.post(
            f'{self.account.hq}/build/threats/{threat_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_threat(self, threat_id, purge):
        """ Delete an existing threat """
        res = requests.delete(
            f'{self.account.hq}/build/threats/{threat_id}',
            json=dict(purge=purge),
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_detection(self, rules: dict, test_id: str, partner: Control, detection_id=None, rule_id=None):
        """ Create a detection """
        body = dict(rules=rules, test_id=test_id, control=partner.name)
        if detection_id:
            body['detection_id'] = detection_id
        if rule_id:
            body['rule_id'] = rule_id

        res = requests.post(
            f'{self.account.hq}/build/detections',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_detection(self, detection_id: str, rules=None, test_id=None):
        """ Update a detection """
        body = dict()
        if rules:
            body['rules'] = rules
        if test_id:
            body['test_id'] = test_id

        res = requests.post(
            f'{self.account.hq}/build/detections/{detection_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_detection(self, detection_id: str):
        """ Delete an existing detection """
        res = requests.delete(
            f'{self.account.hq}/build/detections/{detection_id}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
