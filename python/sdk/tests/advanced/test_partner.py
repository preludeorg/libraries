import os
import json
import pytest
import requests
import time

from datetime import datetime, timedelta, timezone
from prelude_sdk.models.codes import Control
from prelude_sdk.controllers.iam_controller import IAMAccountController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.partner_controller import PartnerController

from testutils import *


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    if metafunc.cls is TestPartnerAttach:
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            if not (scenario[1]["partner_api"] or scenario[1]["user"]):
                argvalues.append(
                    pytest.param(
                        *[x[1] for x in items],
                        marks=pytest.mark.skip("Creds not supplied"),
                    )
                )
            else:
                argvalues.append([x[1] for x in items])
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


@pytest.mark.order(7)
@pytest.mark.usefixtures("setup_account")
class TestPartnerAttach:
    scenarios = [
        (
            c.name,
            dict(
                control=c,
                partner_api=os.getenv(f"{c.name.upper()}_API") or "",
                user=os.getenv(f"{c.name.upper()}_USER") or "",
                secret=os.getenv(f"{c.name.upper()}_SECRET") or "",
            ),
        )
        for c in Control
        if c.value > 0
    ]

    def setup_class(self):
        self.iam = IAMAccountController(pytest.account)
        self.detect = DetectController(pytest.account)
        self.partner = PartnerController(pytest.account)

    def test_attach(self, control, partner_api, user, secret):
        res = unwrap(self.partner.attach)(
            self.partner, partner=control, api=partner_api, user=user, secret=secret
        )
        expected = dict(api=partner_api, connected=True)
        assert expected == res

    def test_get_account(self, control, partner_api, user, secret):
        res = unwrap(self.iam.get_account)(self.iam)
        [r.pop("created") for r in res["controls"]]
        pytest.controls = {c["id"]: c["instance_id"] for c in res["controls"]}
        expected = dict(
            api=partner_api,
            id=control.value,
            instance_id=pytest.controls[control.value],
            max_groups=30,
            name="",
            username=user,
        )
        assert expected in res["controls"]

    @pytest.mark.order(-8)
    def test_detach(self, control, partner_api, user, secret):
        unwrap(self.partner.detach)(
            self.partner, partner=control, instance_id=pytest.controls[control.value]
        )
        res = unwrap(self.iam.get_account)(self.iam)
        for c in res["controls"]:
            assert c["id"] != control.value
        pytest.controls.pop(control.value, None)


@pytest.mark.order(8)
@pytest.mark.usefixtures(
    "setup_account", "setup_test", "setup_detection", "setup_threat_hunt"
)
class EDRPartner:
    def setup_class(self):
        self.detect = DetectController(pytest.account)
        self.jobs = JobsController(pytest.account)
        self.partner = PartnerController(pytest.account)

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self):
        if self.control.value not in pytest.controls:
            pytest.skip(f"{self.control.name} not attached")
        yield

    def test_create_endpoint(self):
        pytest.token = self.detect.register_endpoint(
            host=self.host,
            serial_num=self.host,
            reg_string=f"{pytest.expected_account['account_id']}/{pytest.service_user_token}",
        )
        pytest.endpoint = dict(
            host=self.host,
            serial_num=self.host,
            edr_id=self.edr_id,
            control=self.control.value,
            tags=[],
            dos=None,
            os=self.os,
            policy=self.policy,
            policy_name=self.policy_name,
        )

    def test_list_endpoints(self):
        def _open_sync_jobs():
            result = unwrap(self.jobs.job_statuses)(self.jobs)
            return any(
                job["end_time"] is None
                for job in result["PRELUDE_ENDPOINT_SYNC"]
                if job["control"] == self.control.value
            )

        time.sleep(2)
        while _open_sync_jobs():
            time.sleep(2)

        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert len(res) >= 1
        sorted_res = {r["serial_num"]: r for r in res}
        pytest.endpoint["endpoint_id"] = sorted_res[pytest.endpoint["serial_num"]][
            "endpoint_id"
        ]
        expected = {pytest.endpoint["serial_num"]: pytest.endpoint}
        diffs = check_dict_items(expected, sorted_res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_partner_endpoints(self):
        res = unwrap(self.partner.endpoints)(
            self.partner,
            partner=self.control,
            platform=self.platform,
            hostname=self.host,
        )
        expected = {self.edr_id: {"hostname": self.host.lower(), "os": self.os}}
        if self.policy:
            expected[self.edr_id]["policy"] = self.policy
            expected[self.edr_id]["policy_name"] = self.policy_name
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_activity_logs(self, api):
        res = requests.get(
            api,
            headers=dict(
                token=pytest.token,
                dos=f"{self.platform}-x86_64",
                dat=f"{pytest.test_id}:100",
                version="2.7",
            ),
        )
        assert res.status_code in [200, 302]
        pytest.endpoint["dos"] = f"{self.platform}-x86_64"

        filters = dict(
            start=datetime.now(timezone.utc) - timedelta(days=1),
            finish=datetime.now(timezone.utc) + timedelta(days=1),
            endpoints=pytest.endpoint["endpoint_id"],
            tests=pytest.test_id,
        )
        res = unwrap(self.detect.describe_activity)(
            self.detect, view="logs", filters=filters
        )
        assert len(res) == 1, json.dumps(res, indent=2)
        expected = dict(
            test=pytest.test_id,
            endpoint_id=pytest.endpoint["endpoint_id"],
            status=100,
            dos=pytest.endpoint["dos"],
            control=self.control.value,
            os=self.os,
            policy=self.policy,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_do_threat_hunt(self):
        if self.control == Control.SENTINELONE:
            pytest.skip("Threat hunts not supported for SENTINELONE")
        if not pytest.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        threat_hunt_id = (
            pytest.crwd_threat_hunt_id
            if self.control == Control.CROWDSTRIKE
            else pytest.mde_threat_hunt_id
        )
        res = unwrap(self.detect.do_threat_hunt)(
            self.detect, threat_hunt_id=threat_hunt_id
        )
        assert {
            "account_id",
            "non_prelude_origin",
            "prelude_origin",
            "threat_hunt_id",
        } == set(res.keys())
        assert res["account_id"] == pytest.expected_account["account_id"]
        assert res["threat_hunt_id"] == threat_hunt_id
        pytest.non_prelude_origin = res["non_prelude_origin"]
        pytest.prelude_origin = res["prelude_origin"]

    def test_threat_hunt_activity(self):
        if self.control == Control.SENTINELONE:
            pytest.skip("Threat hunts not supported for SENTINELONE")
        if not pytest.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        threat_hunt_id = (
            pytest.crwd_threat_hunt_id
            if self.control == Control.CROWDSTRIKE
            else pytest.mde_threat_hunt_id
        )
        res = unwrap(self.detect.threat_hunt_activity)(
            self.detect, threat_hunt_id=threat_hunt_id
        )
        expected = dict(
            non_prelude_origin=pytest.non_prelude_origin,
            prelude_origin=pytest.prelude_origin,
            test_id=pytest.test_id,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_block(self):
        if self.control == Control.SENTINELONE:
            pytest.skip("Partner block not supported for SENTINELONE")
        if not pytest.expected_account["features"]["detections"]:
            pytest.skip("DETECTIONS feature not enabled")
        res = unwrap(self.partner.block)(
            self.partner, partner=self.control, test_id=pytest.test_id
        )
        assert res[0]["group_id"] == self.group_id
        assert (
            res[0]["platform"]
            == pytest.expected_detection["rule"]["logsource"]["product"]
        )

        first_rule = res[0]["rules"][0]
        expected_name_suffix = (
            "(0)" if self.control == Control.CROWDSTRIKE else "- windows"
        )
        assert (
            first_rule["name"]
            == f'{pytest.expected_test["name"]} ({pytest.detection_id[:8]}) {expected_name_suffix}'
        )
        assert first_rule["status"] == "CREATED", json.dumps(first_rule, indent=2)
        assert (
            first_rule.get("ioa_id")
            if self.control == Control.CROWDSTRIKE
            else first_rule.get("custom_detection_id")
        )

    def test_reports(self):
        if self.control != Control.CROWDSTRIKE:
            pytest.skip("IOA reports only supported for CROWDSTRIKE")
        if not pytest.expected_account["features"]["detections"]:
            pytest.skip("DETECTIONS feature not enabled")

        res = unwrap(self.partner.list_reports)(
            self.partner, partner=self.control, test_id=pytest.test_id
        )
        assert 1 == len(res)
        expected = dict(
            blocked=0,
            detected=0,
            detection_id=pytest.detection_id,
            group_id=self.group_id,
            monitored=0,
            platform=pytest.expected_detection["rule"]["logsource"]["product"],
            test_id=pytest.test_id,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_observed_detected(self):
        if self.control == Control.SENTINELONE:
            pytest.skip("Observed detected not supported for SENTINELONE")
        if not pytest.expected_account["features"]["observed_detected"]:
            pytest.skip("OBSERVED_DETECTED feature not enabled")

        res = unwrap(self.partner.observed_detected)(self.partner)

        assert self.control.name in res
        assert 1 <= len(res[self.control.name])
        assert {"account_id", "detected", "endpoint_ids", "observed", "test_id"} == set(
            res[self.control.name][0].keys()
        )
        assert (
            res[self.control.name][0]["account_id"]
            == pytest.expected_account["account_id"]
        )

    def test_ioa_stats(self):
        try:
            if self.control != Control.CROWDSTRIKE:
                pytest.skip("IOA stats only supported for CROWDSTRIKE")
            if not pytest.expected_account["features"]["observed_detected"]:
                pytest.skip("OBSERVED_DETECTED feature not enabled")

            res = unwrap(self.partner.ioa_stats)(self.partner)
            assert 0 == len(res)
        finally:
            unwrap(self.detect.delete_endpoint)(
                self.detect, ident=pytest.endpoint["endpoint_id"]
            )

    def test_list_advisories(self):
        if self.control != Control.CROWDSTRIKE:
            pytest.skip("List advisories only supported for CROWDSTRIKE")
        if not pytest.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        res = unwrap(self.partner.list_advisories)(
            self.partner, partner=self.control, limit=5, offset=0
        )
        assert 1 <= len(res["advisories"])
        assert res["advisories"][0]["id"]
        assert {"created", "description", "id", "name", "tags", "slug"} == set(
            res["advisories"][0].keys()
        )
        assert res["pagination"]["limit"] == 5
        assert res["pagination"]["offset"] == 0
        assert res["pagination"]["total"] > 0
        pytest.crowdstrike_advisory_id = res["advisories"][0]["id"]


crowdstrike = dict(
    host=os.getenv("CROWDSTRIKE_HOST"),
    edr_id=os.getenv("CROWDSTRIKE_EDR_ID"),
    control=Control.CROWDSTRIKE,
    os=os.getenv("CROWDSTRIKE_OS"),
    platform=os.getenv("CROWDSTRIKE_PLATFORM"),
    policy=os.getenv("CROWDSTRIKE_POLICY"),
    policy_name=os.getenv("CROWDSTRIKE_POLICY_NAME"),
    group_id=os.getenv("CROWDSTRIKE_WINDOWS_IOA_GROUP_ID"),
)

defender = dict(
    host=os.getenv("DEFENDER_HOST"),
    edr_id=os.getenv("DEFENDER_EDR_ID"),
    control=Control.DEFENDER,
    os=os.getenv("DEFENDER_OS"),
    platform=os.getenv("DEFENDER_PLATFORM"),
    policy=None,
    policy_name=None,
    group_id=None,
)

sentinel_one = dict(
    host=os.getenv("S1_HOST"),
    edr_id=os.getenv("S1_EDR_ID"),
    control=Control.SENTINELONE,
    os=os.getenv("S1_OS"),
    platform=os.getenv("S1_PLATFORM"),
    policy=os.getenv("S1_POLICY"),
    policy_name=os.getenv("S1_POLICY_NAME"),
    group_id=None,
)

for params in [crowdstrike, defender, sentinel_one]:
    cls = type(f"TestEDRPartner_{params['control'].name}", (EDRPartner,), params)
    globals()[cls.__name__] = cls
