import urllib

from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control, EDRResponse


class BuildController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def clone_test(self, source_test_id):
        """Clone a test"""
        res = self.post(
            f"{self.account.hq}/build/tests", json=dict(source_test_id=source_test_id)
        )
        return res.json()

    @verify_credentials
    def create_test(self, name, unit, schedulable=None, technique=None, test_id=None):
        """Create or update a test"""
        body = dict(name=name, unit=unit)
        if schedulable is not None:
            body["schedulable"] = schedulable
        if technique:
            body["technique"] = technique
        if test_id:
            body["id"] = test_id

        res = self.post(f"{self.account.hq}/build/tests", json=body)
        return res.json()

    @verify_credentials
    def update_test(
        self,
        test_id,
        crowdstrike_expected_outcome: EDRResponse = None,
        name=None,
        schedulable=None,
        technique=None,
        unit=None,
    ):
        """Update a test"""
        body = dict()
        if crowdstrike_expected_outcome:
            body["expected"] = dict(crowdstrike=crowdstrike_expected_outcome.value)
        if name:
            body["name"] = name
        if schedulable is not None:
            body["schedulable"] = schedulable
        if technique is not None:
            body["technique"] = technique
        if unit:
            body["unit"] = unit

        res = self.post(f"{self.account.hq}/build/tests/{test_id}", json=body)
        return res.json()

    @verify_credentials
    def delete_test(self, test_id, purge):
        """Delete an existing test"""
        res = self.delete(
            f"{self.account.hq}/build/tests/{test_id}", json=dict(purge=purge)
        )
        return res.json()

    @verify_credentials
    def undelete_test(self, test_id):
        """Undelete a tombstoned test"""
        res = self.post(f"{self.account.hq}/build/tests/{test_id}/undelete")
        return res.json()

    @verify_credentials
    def upload(self, test_id, filename, data, skip_compile=False):
        """Upload a test or attachment"""
        if len(data) > 3145728:
            raise ValueError(f"File size must be under 3MB ({filename})")

        h = self.account.headers | {"Content-Type": "application/octet-stream"}
        query_params = ""
        if skip_compile:
            query_params = "?" + urllib.parse.urlencode(dict(skip_compile=True))

        res = self.post(
            f"{self.account.hq}/build/tests/{test_id}/{filename}{query_params}",
            data=data,
            headers=h,
        )
        return res.json()

    @verify_credentials
    def compile_code_string(self, code: str, source_test_id: str = None):
        """Compile a code string"""
        res = self.post(
            f"{self.account.hq}/build/compile",
            json=dict(code=code, source_test_id=source_test_id),
        )
        return res.json()

    @verify_credentials
    def get_compile_status(self, job_id):
        res = self.get(f"{self.account.hq}/build/compile/{job_id}")
        return res.json()

    @verify_credentials
    def create_threat(
        self,
        name,
        published,
        schedulable=None,
        source=None,
        source_id=None,
        tests=None,
        threat_id=None,
    ):
        """Create a threat"""
        body = dict(name=name, published=published)
        if schedulable is not None:
            body["schedulable"] = schedulable
        if source:
            body["source"] = source
        if source_id:
            body["source_id"] = source_id
        if tests:
            body["tests"] = tests
        if threat_id:
            body["id"] = threat_id

        res = self.post(f"{self.account.hq}/build/threats", json=body)
        return res.json()

    @verify_credentials
    def update_threat(
        self,
        threat_id,
        name=None,
        published=None,
        schedulable=None,
        source=None,
        source_id=None,
        tests=None,
    ):
        """Update a threat"""
        body = dict()
        if name:
            body["name"] = name
        if published is not None:
            body["published"] = published
        if schedulable is not None:
            body["schedulable"] = schedulable
        if source is not None:
            body["source"] = source
        if source_id is not None:
            body["source_id"] = source_id
        if tests is not None:
            body["tests"] = tests

        res = self.post(f"{self.account.hq}/build/threats/{threat_id}", json=body)
        return res.json()

    @verify_credentials
    def delete_threat(self, threat_id, purge):
        """Delete an existing threat"""
        res = self.delete(
            f"{self.account.hq}/build/threats/{threat_id}",
            json=dict(purge=purge),
        )
        return res.json()

    @verify_credentials
    def undelete_threat(self, threat_id):
        """Undelete a tombstoned threat"""
        res = self.post(f"{self.account.hq}/build/threats/{threat_id}/undelete")
        return res.json()

    @verify_credentials
    def create_detection(
        self, rule: str, test_id: str, detection_id=None, rule_id=None
    ):
        """Create a detection"""
        body = dict(rule=rule, test_id=test_id)
        if detection_id:
            body["detection_id"] = detection_id
        if rule_id:
            body["rule_id"] = rule_id

        res = self.post(f"{self.account.hq}/build/detections", json=body)
        return res.json()

    @verify_credentials
    def update_detection(self, detection_id: str, rule=None, test_id=None):
        """Update a detection"""
        body = dict()
        if rule:
            body["rule"] = rule
        if test_id:
            body["test_id"] = test_id

        res = self.post(f"{self.account.hq}/build/detections/{detection_id}", json=body)
        return res.json()

    @verify_credentials
    def delete_detection(self, detection_id: str):
        """Delete an existing detection"""
        res = self.delete(f"{self.account.hq}/build/detections/{detection_id}")
        return res.json()

    @verify_credentials
    def create_threat_hunt(
        self,
        control: Control,
        test_id: str,
        name: str,
        query: str,
        threat_hunt_id: str = None,
    ):
        """Create a threat hunt"""
        body = dict(
            control=control.name,
            name=name,
            query=query,
            test_id=test_id,
        )
        if threat_hunt_id:
            body["id"] = threat_hunt_id

        res = self.post(f"{self.account.hq}/build/threat_hunts", json=body)
        threat_hunt = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunt, [(Control, "control")])
        return threat_hunt

    @verify_credentials
    def update_threat_hunt(
        self,
        threat_hunt_id: str,
        name: str = None,
        query: str = None,
        test_id: str = None,
    ):
        """Update a threat hunt"""
        body = dict()
        if name:
            body["name"] = name
        if query:
            body["query"] = query
        if test_id:
            body["test_id"] = test_id

        res = self.post(
            f"{self.account.hq}/build/threat_hunts/{threat_hunt_id}", json=body
        )
        threat_hunt = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunt, [(Control, "control")])
        return threat_hunt

    @verify_credentials
    def delete_threat_hunt(self, threat_hunt_id: str):
        """Delete an existing threat hunt"""
        res = self.delete(f"{self.account.hq}/build/threat_hunts/{threat_hunt_id}")
        return res.json()
