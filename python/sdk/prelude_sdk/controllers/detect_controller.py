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
        )
        return res.text

    @verify_credentials
    def update_endpoint(self, endpoint_id, tags=None):
        """Update an endpoint in your account"""
        body = dict()
        if tags is not None:
            body["tags"] = tags

        res = self.post(f"{self.account.hq}/detect/endpoint/{endpoint_id}", json=body)
        return res.json()

    @verify_credentials
    def delete_endpoint(self, ident: str):
        """Delete an endpoint from your account"""
        params = dict(id=ident)

        res = self.delete(f"{self.account.hq}/detect/endpoint", json=params)
        return res.json()

    @verify_credentials
    def list_endpoints(self, days: int = 90):
        """List all endpoints on your account"""
        params = dict(days=days)

        res = self.get(f"{self.account.hq}/detect/endpoint", params=params)
        endpoints = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(endpoints, [(Control, "control")])
        return endpoints

    @verify_credentials
    def describe_activity(self, filters: dict, view: str = "protected"):
        """Get report for an Account"""
        params = dict(view=view, **filters)

        res = self.get(f"{self.account.hq}/detect/activity", params=params)
        return res.json()

    @verify_credentials
    def threat_hunt_activity(self, threat_hunt_id=None, test_id=None, threat_id=None):
        """Get threat hunt activity"""
        params = dict(
            threat_hunt_id=threat_hunt_id, test_id=test_id, threat_id=threat_id
        )

        res = self.get(f"{self.account.hq}/detect/threat_hunt_activity", params=params)
        return res.json()

    @verify_credentials
    def list_tests(self, filters: dict = None):
        """List all tests available to an account"""
        res = self.get(
            f"{self.account.hq}/detect/tests", params=filters if filters else {}
        )
        return res.json()

    @verify_credentials
    def get_test(self, test_id):
        """Get properties of an existing test"""
        res = self.get(f"{self.account.hq}/detect/tests/{test_id}")
        return res.json()

    @verify_credentials
    def list_techniques(self):
        """List techniques"""
        res = self.get(f"{self.account.hq}/detect/techniques")
        return res.json()

    @verify_credentials
    def list_threats(self):
        """List threats"""
        res = self.get(
            f"{self.account.hq}/detect/threats",
        )
        return res.json()

    @verify_credentials
    def get_threat(self, threat_id):
        """Get properties of an existing threat"""
        res = self.get(f"{self.account.hq}/detect/threats/{threat_id}")
        return res.json()

    @verify_credentials
    def list_detections(self):
        """List detections"""
        res = self.get(f"{self.account.hq}/detect/detections")
        return res.json()

    @verify_credentials
    def get_detection(self, detection_id):
        """Get properties of an existing detection"""
        res = self.get(f"{self.account.hq}/detect/detections/{detection_id}")
        return res.json()

    @verify_credentials
    def list_threat_hunts(self, filters: dict = None):
        """List threat hunts"""
        res = self.get(
            f"{self.account.hq}/detect/threat_hunts", params=filters if filters else {}
        )
        threat_hunts = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunts, [(Control, "control")])
        return threat_hunts

    @verify_credentials
    def get_threat_hunt(self, threat_hunt_id):
        """Get properties of an existing threat hunt"""
        res = self.get(f"{self.account.hq}/detect/threat_hunts/{threat_hunt_id}")
        threat_hunt = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(threat_hunt, [(Control, "control")])
        return threat_hunt

    @verify_credentials
    def do_threat_hunt(self, threat_hunt_id):
        """Run a threat hunt"""
        res = self.post(
            f"{self.account.hq}/detect/threat_hunts/{threat_hunt_id}", timeout=30
        )
        return res.json()

    @verify_credentials
    def download(self, test_id, filename):
        """Clone a test file or attachment"""
        res = self.get(f"{self.account.hq}/detect/tests/{test_id}/{filename}")
        return res.content

    @verify_credentials
    def schedule(self, items: list):
        """
        Schedule tests and threats so endpoints will start running them

        Example: items=[dict(run_code='DAILY', tags='grp-1,grp2', test_id='123-123-123'),
                        dict(run_code='DAILY', tags='grp-1', threat_id='abc-def-ghi')]
        """
        body = dict(items=items)

        res = self.post(url=f"{self.account.hq}/detect/queue", json=body)
        schedule = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(schedule, [(RunCode, "run_code")])
        return schedule

    @verify_credentials
    def unschedule(self, items: list):
        """
        Unschedule tests and threats so endpoints will stop running them

        Example: items=[dict(tags='grp-1,grp2', test_id='123-123-123'),
                        dict(tags='grp-1', threat_id='abc-def-ghi')]
        """
        body = dict(items=items)

        res = self.delete(f"{self.account.hq}/detect/queue", json=body)
        return res.json()

    @verify_credentials
    def accept_terms(self, name, version):
        """Accept terms and conditions"""
        body = dict(name=name, version=version)

        res = self.post(f"{self.account.hq}/iam/terms", json=body)
        return res.json()
