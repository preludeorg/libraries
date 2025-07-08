from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control, RunCode


class DetectController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    def register_endpoint(self, host, serial_num, reg_string, tags=None):
        """Register (or re-register) an endpoint to your account"""
        body = dict(id=f"{host}:{serial_num}")
        if tags:
            body["tags"] = tags
        account, token = reg_string.split("/")

        res = self._session.post(
            f"{self.account.hq}/detect/endpoint",
            headers=dict(account=account, token=token, _product="py-sdk"),
            json=body,
            timeout=10,
        )
        return res.text

    @verify_credentials
    def update_endpoint(self, endpoint_id, tags=None):
        """Update an endpoint in your account"""
        body = dict()
        if tags is not None:
            body["tags"] = tags

        res = self.post(
            f"{self.account.hq}/detect/endpoint/{endpoint_id}",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_endpoint(self, ident: str):
        """Delete an endpoint from your account"""
        params = dict(id=ident)
        res = self.delete(
            f"{self.account.hq}/detect/endpoint",
            headers=self.account.headers,
            json=params,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_endpoints(self, days: int = 90):
        """List all endpoints on your account"""
        params = dict(days=days)
        res = self.get(
            f"{self.account.hq}/detect/endpoint",
            headers=self.account.headers,
            params=params,
            timeout=10,
        )
        endpoints = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(endpoints, [(Control, "control")])
        return endpoints

    @verify_credentials
    def describe_activity(self, filters: dict, view: str = "protected"):
        """Get report for an Account"""
        params = dict(view=view, **filters)
        res = self.get(
            f"{self.account.hq}/detect/activity",
            headers=self.account.headers,
            params=params,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def threat_hunt_activity(self, threat_hunt_id=None, test_id=None, threat_id=None):
        """Get threat hunt activity"""
        filters = dict(
            threat_hunt_id=threat_hunt_id, test_id=test_id, threat_id=threat_id
        )
        res = self.get(
            f"{self.account.hq}/detect/threat_hunt_activity",
            headers=self.account.headers,
            params=filters,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_tests(self, filters: dict = None):
        """List all tests available to an account"""
        res = self.get(
            f"{self.account.hq}/detect/tests",
            headers=self.account.headers,
            params=filters if filters else {},
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def get_test(self, test_id):
        """Get properties of an existing test"""
        res = self.get(
            f"{self.account.hq}/detect/tests/{test_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_techniques(self):
        """List techniques"""
        res = self.get(
            f"{self.account.hq}/detect/techniques",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_threats(self):
        """List threats"""
        res = self.get(
            f"{self.account.hq}/detect/threats",
            headers=self.account.headers,
            params={},
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def get_threat(self, threat_id):
        """Get properties of an existing threat"""
        res = self.get(
            f"{self.account.hq}/detect/threats/{threat_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_detections(self):
        """List detections"""
        res = self.get(
            f"{self.account.hq}/detect/detections",
            headers=self.account.headers,
            params={},
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def get_detection(self, detection_id):
        """Get properties of an existing detection"""
        res = self.get(
            f"{self.account.hq}/detect/detections/{detection_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_threat_hunts(self, filters: dict = None):
        """List threat hunts"""
        res = self.get(
            f"{self.account.hq}/detect/threat_hunts",
            headers=self.account.headers,
            params=filters if filters else {},
            timeout=10,
        )
        threat_hunts = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunts, [(Control, "control")])
        return threat_hunts

    @verify_credentials
    def get_threat_hunt(self, threat_hunt_id):
        """Get properties of an existing threat hunt"""
        res = self.get(
            f"{self.account.hq}/detect/threat_hunts/{threat_hunt_id}",
            headers=self.account.headers,
            timeout=10,
        )
        threat_hunt = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunt, [(Control, "control")])
        return threat_hunt

    @verify_credentials
    def do_threat_hunt(self, threat_hunt_id):
        """Run a threat hunt"""
        res = self.post(
            f"{self.account.hq}/detect/threat_hunts/{threat_hunt_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def download(self, test_id, filename):
        """Clone a test file or attachment"""
        res = self.get(
            f"{self.account.hq}/detect/tests/{test_id}/{filename}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.content

    @verify_credentials
    def schedule(self, items: list):
        """Schedule tests and threats so endpoints will start running them

        Example: items=[dict(run_code='DAILY', tags='grp-1,grp2', test_id='123-123-123'),
                        dict(run_code='DAILY', tags='grp-1', threat_id='abc-def-ghi')]
        """
        res = self.post(
            url=f"{self.account.hq}/detect/queue",
            headers=self.account.headers,
            json=dict(items=items),
            timeout=10,
        )
        schedule = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(schedule, [(RunCode, "run_code")])
        return schedule

    @verify_credentials
    def unschedule(self, items: list):
        """Unschedule tests and threats so endpoints will stop running them

        Example: items=[dict(tags='grp-1,grp2', test_id='123-123-123'),
                        dict(tags='grp-1', threat_id='abc-def-ghi')]
        """
        res = self.delete(
            f"{self.account.hq}/detect/queue",
            headers=self.account.headers,
            json=dict(items=items),
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def accept_terms(self, name, version):
        """Accept terms and conditions"""
        res = self.post(
            f"{self.account.hq}/iam/terms",
            headers=self.account.headers,
            json=dict(name=name, version=version),
            timeout=10,
        )
        return res.json()
