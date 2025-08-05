import os
import json
import logging
import pytest
import requests
import time

from datetime import datetime, timedelta, timezone

from prelude_sdk.models.codes import Control
from testutils import *


@pytest.mark.stage2
@pytest.mark.order(8)
class PartnerAttach:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        if not (cls.partner_api or cls.user):
            pytest.skip("Creds not supplied")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )

    def test_attach(self, partner):
        res = unwrap(partner.attach)(
            partner,
            partner=self.control,
            api=self.partner_api,
            user=self.user,
            secret=self.secret,
        )
        expected = dict(api=self.partner_api, connected=True)
        assert expected == res

    def test_get_account(self, iam_account):
        res = unwrap(iam_account.get_account)(iam_account)
        [r.pop("created") for r in res["controls"]]
        controls = {c["id"]: c["instance_id"] for c in res["controls"]}
        expected = dict(
            api=self.partner_api,
            id=self.control.value,
            instance_id=controls[self.control.value],
            max_groups=30,
            name="",
            username=self.user,
        )
        assert expected in res["controls"]


for control in Control:
    if control.value > 0 and not control.parent:
        cls = type(
            f"TestPartnerAttach_{control.name}",
            (PartnerAttach,),
            dict(
                control=control,
                partner_api=os.getenv(f"{control.name.upper()}_API") or "",
                user=os.getenv(f"{control.name.upper()}_USER") or "",
                secret=os.getenv(f"{control.name.upper()}_SECRET") or "",
            ),
        )
        globals()[cls.__name__] = cls


@pytest.mark.stage3
@pytest.mark.order(7)
class EDRPartner:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        controls = {c["id"] for c in cls.expected_account["controls"]}
        if cls.control.value not in controls:
            pytest.skip(f"{cls.control.name} not attached")

        cls.test = request.getfixturevalue("my_test")
        assert cls.test, "No test found for EDR tests"
        cls.test_id = cls.test["id"]
        cls.crwd_threat_hunt_id, cls.mde_threat_hunt_id = request.getfixturevalue(
            "my_threat_hunt_ids"
        )
        cls.detection = request.getfixturevalue("my_detection")

        cls.state = dict()

    def test_create_endpoint(self, detect, service_user_token):
        self.state["endpoint_token"] = detect.register_endpoint(
            host=self.host,
            serial_num=self.host,
            reg_string=f"{self.expected_account['account_id']}/{service_user_token}",
        )
        self.state["endpoint"] = dict(
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

    def test_list_endpoints(self, detect, jobs):
        def _open_sync_jobs():
            result = unwrap(jobs.job_statuses)(jobs)
            return any(
                job["end_time"] is None
                for job in result["PRELUDE_ENDPOINT_SYNC"]
                if job["control"] == self.control.value
            )

        time.sleep(2)
        while _open_sync_jobs():
            time.sleep(2)

        res = unwrap(detect.list_endpoints)(detect)
        assert len(res) >= 1
        sorted_res = {r["serial_num"]: r for r in res}
        self.state["endpoint"]["endpoint_id"] = sorted_res[
            self.state["endpoint"]["serial_num"]
        ]["endpoint_id"]
        expected = {self.state["endpoint"]["serial_num"]: self.state["endpoint"]}
        diffs = check_dict_items(expected, sorted_res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_partner_endpoints(self, partner):
        res = unwrap(partner.endpoints)(
            partner, partner=self.control, platform=self.platform, hostname=self.host
        )
        expected = {self.edr_id: {"hostname": self.host.lower(), "os": self.os}}
        if self.policy:
            expected[self.edr_id]["policy"] = self.policy
            expected[self.edr_id]["policy_name"] = self.policy_name
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_activity_logs(self, detect, api):
        res = requests.get(
            api,
            headers=dict(
                token=self.state["endpoint_token"],
                dos=f"{self.platform}-x86_64",
                dat=f"{self.test_id}:100",
                version="2.7",
            ),
        )
        assert res.status_code in [200, 302]
        self.state["endpoint"]["dos"] = f"{self.platform}-x86_64"

        filters = dict(
            start=datetime.now(timezone.utc) - timedelta(days=1),
            finish=datetime.now(timezone.utc) + timedelta(days=1),
            endpoints=self.state["endpoint"]["endpoint_id"],
            tests=self.test_id,
        )
        res = unwrap(detect.describe_activity)(detect, view="logs", filters=filters)
        assert len(res) == 1, json.dumps(res, indent=2)
        expected = dict(
            test=self.test_id,
            endpoint_id=self.state["endpoint"]["endpoint_id"],
            status=100,
            dos=self.state["endpoint"]["dos"],
            control=self.control.value,
            os=self.os,
            policy=self.policy,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_do_threat_hunt(self, detect):
        if self.control == Control.SENTINELONE:
            pytest.skip("Threat hunts not supported for SENTINELONE")
        if not self.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        threat_hunt_id = (
            self.crwd_threat_hunt_id
            if self.control == Control.CROWDSTRIKE
            else self.mde_threat_hunt_id
        )
        res = unwrap(detect.do_threat_hunt)(detect, threat_hunt_id=threat_hunt_id)
        assert {
            "account_id",
            "non_prelude_origin",
            "prelude_origin",
            "threat_hunt_id",
        } == set(res.keys())
        assert res["account_id"] == self.expected_account["account_id"]
        assert res["threat_hunt_id"] == threat_hunt_id
        self.state["non_prelude_origin"] = res["non_prelude_origin"]
        self.state["prelude_origin"] = res["prelude_origin"]

    def test_threat_hunt_activity(self, detect):
        if self.control == Control.SENTINELONE:
            pytest.skip("Threat hunts not supported for SENTINELONE")
        if not self.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        threat_hunt_id = (
            self.crwd_threat_hunt_id
            if self.control == Control.CROWDSTRIKE
            else self.mde_threat_hunt_id
        )
        res = unwrap(detect.threat_hunt_activity)(detect, threat_hunt_id=threat_hunt_id)
        expected = dict(
            non_prelude_origin=self.state["non_prelude_origin"],
            prelude_origin=self.state["prelude_origin"],
            test_id=self.test_id,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_block(self, partner):
        if self.control == Control.SENTINELONE:
            pytest.skip("Partner block not supported for SENTINELONE")
        if not self.expected_account["features"]["detections"]:
            pytest.skip("DETECTIONS feature not enabled")
        res = unwrap(partner.block)(partner, partner=self.control, test_id=self.test_id)
        assert res[0]["group_id"] == self.group_id
        assert res[0]["platform"] == self.detection["rule"]["logsource"]["product"]

        first_rule = res[0]["rules"][0]
        expected_name_suffix = (
            "(0)" if self.control == Control.CROWDSTRIKE else "- windows"
        )
        assert (
            first_rule["name"]
            == f'{self.test["name"]} ({self.detection["id"][:8]}) {expected_name_suffix}'
        )
        assert first_rule["status"] == "CREATED", json.dumps(first_rule, indent=2)
        assert (
            first_rule.get("ioa_id")
            if self.control == Control.CROWDSTRIKE
            else first_rule.get("custom_detection_id")
        )

    def test_reports(self, partner):
        if self.control != Control.CROWDSTRIKE:
            pytest.skip("IOA reports only supported for CROWDSTRIKE")
        if not self.expected_account["features"]["detections"]:
            pytest.skip("DETECTIONS feature not enabled")

        res = unwrap(partner.list_reports)(
            partner, partner=self.control, test_id=self.test_id
        )
        assert 1 == len(res)
        expected = dict(
            blocked=0,
            detected=0,
            detection_id=self.detection["id"],
            group_id=self.group_id,
            monitored=0,
            platform=self.detection["rule"]["logsource"]["product"],
            test_id=self.test_id,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_observed_detected(self, partner):
        if self.control == Control.SENTINELONE:
            pytest.skip("Observed detected not supported for SENTINELONE")
        if not self.expected_account["features"]["observed_detected"]:
            pytest.skip("OBSERVED_DETECTED feature not enabled")

        res = unwrap(partner.observed_detected)(partner)

        assert self.control.name in res
        assert 1 <= len(res[self.control.name])
        assert {"account_id", "detected", "endpoint_ids", "observed", "test_id"} == set(
            res[self.control.name][0].keys()
        )
        assert (
            res[self.control.name][0]["account_id"]
            == self.expected_account["account_id"]
        )

    def test_ioa_stats(self, detect, partner):
        try:
            if self.control != Control.CROWDSTRIKE:
                pytest.skip("IOA stats only supported for CROWDSTRIKE")
            if not self.expected_account["features"]["observed_detected"]:
                pytest.skip("OBSERVED_DETECTED feature not enabled")

            res = unwrap(partner.ioa_stats)(partner)
            assert 0 == len(res)
        finally:
            unwrap(detect.delete_endpoint)(
                detect, ident=self.state["endpoint"]["endpoint_id"]
            )


crowdstrike = dict(
    host=os.getenv("CROWDSTRIKE_HOST"),
    edr_id=os.getenv("CROWDSTRIKE_EDR_ID"),
    control=Control.CROWDSTRIKE,
    os=os.getenv("CROWDSTRIKE_OS"),
    platform=os.getenv("CROWDSTRIKE_PLATFORM"),
    policy=os.getenv("CROWDSTRIKE_POLICY"),
    policy_name=os.getenv("CROWDSTRIKE_POLICY_NAME"),
    webhook_keys=None,
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
    webhook_keys=None,
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
    webhook_keys={"url", "description", "secret", "headers"},
    group_id=None,
)

for params in [crowdstrike, defender, sentinel_one]:
    cls = type(f"TestEDRPartner_{params['control'].name}", (EDRPartner,), params)
    globals()[cls.__name__] = cls
