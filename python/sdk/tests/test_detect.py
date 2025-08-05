import json
import logging
import os
import pytest
import requests
from datetime import datetime, timedelta, timezone

from dateutil.parser import parse

from prelude_sdk.models.codes import RunCode
from testutils import *


@pytest.mark.stage3
@pytest.mark.order(7)
class TestDetect:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        cls.test_id = request.getfixturevalue("my_test_id")
        assert cls.test_id, "No test found for detect tests"
        cls.threat_id = request.getfixturevalue("my_threat_id")
        assert cls.threat_id, "No threat found for detect tests"

        cls.host = "test_host"
        cls.serial = "test_serial"
        cls.tags = "alpha"
        cls.updated_tags = "beta"
        cls.state = dict()

    def test_list_techniques(self, detect):
        res = unwrap(detect.list_techniques)(detect)
        assert 1 <= len(res)
        assert {
            "category",
            "description",
            "expected",
            "id",
            "name",
            "relevant_categories",
        } == set(res[0].keys())

    def test_register_endpoint(self, detect, service_user_token):
        res = detect.register_endpoint(
            host=self.host,
            serial_num=self.serial,
            reg_string=f"{self.expected_account['account_id']}/{service_user_token}",
            tags=self.tags,
        )
        assert 32 == len(res)

        self.state["endpoint_token"] = res
        self.state["expected_endpoint"] = dict(
            endpoint_id="",
            host=self.host,
            serial_num=self.serial,
            edr_id=None,
            control=0,
            tags=[self.tags],
            dos=None,
            os=None,
            policy=None,
            policy_name=None,
        )

    def test_list_endpoints(self, detect):
        res = unwrap(detect.list_endpoints)(detect)
        assert 1 <= len(res)
        ep = [r for r in res if r["serial_num"] == self.serial][0]
        self.state["expected_endpoint"]["endpoint_id"] = ep["endpoint_id"]
        self.state["endpoint_id"] = ep["endpoint_id"]

        diffs = check_dict_items(self.state["expected_endpoint"], ep)
        assert not diffs, json.dumps(diffs, indent=2)
        assert ep["last_seen"] is None

    def test_update_endpoint(self, detect):
        res = unwrap(detect.update_endpoint)(
            detect, endpoint_id=self.state["endpoint_id"], tags=self.updated_tags
        )
        assert res["id"] == self.state["endpoint_id"]
        self.state["expected_endpoint"]["tags"] = [self.updated_tags]

        res = unwrap(detect.list_endpoints)(detect)
        ep = [r for r in res if r["endpoint_id"] == self.state["endpoint_id"]][0]
        diffs = check_dict_items(self.state["expected_endpoint"], ep)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_schedule_threat(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_length = len(self.expected_account["queue"])

        res = unwrap(detect.schedule)(
            detect, [dict(threat_id=self.threat_id, run_code=RunCode.DAILY.name)]
        )
        self.expected_account["queue"].append(res[0])
        assert 1 == len(res), json.dumps(res, indent=2)
        diffs = check_dict_items(
            dict(threat=self.threat_id, run_code=RunCode.DAILY.value, tag=None),
            res[0],
        )
        assert not diffs, json.dumps(diffs, indent=2)

        queue = sorted(
            unwrap(iam_account.get_account)(iam_account)["queue"],
            key=lambda x: x["started"],
            reverse=True,
        )
        assert queue_length + 1 == len(queue), json.dumps(queue, indent=2)
        expected = dict(threat=self.threat_id, run_code=RunCode.DAILY.value)
        diffs = check_dict_items(expected, queue[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_unschedule_threat(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_length = len(self.expected_account["queue"])

        unwrap(detect.unschedule)(detect, [dict(threat_id=self.threat_id)])
        self.expected_account["queue"] = [
            q for q in self.expected_account["queue"] if q["threat"] != self.threat_id
        ]
        queue = unwrap(iam_account.get_account)(iam_account)["queue"]
        assert queue_length - 1 == len(queue), json.dumps(queue, indent=2)

    def test_schedule_test(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_length = len(self.expected_account["queue"])

        res = unwrap(detect.schedule)(
            detect,
            [
                dict(
                    test_id=self.test_id,
                    run_code=RunCode.DEBUG.name,
                    tags=self.updated_tags,
                )
            ],
        )
        self.expected_account["queue"].append(res[0])
        assert 1 == len(res), json.dumps(res, indent=2)
        diffs = check_dict_items(
            dict(
                test=self.test_id, run_code=RunCode.DEBUG.value, tag=self.updated_tags
            ),
            res[0],
        )
        assert not diffs, json.dumps(diffs, indent=2)

        queue = sorted(
            unwrap(iam_account.get_account)(iam_account)["queue"],
            key=lambda x: x["started"],
            reverse=True,
        )
        assert queue_length + 1 == len(queue), json.dumps(queue, indent=2)
        expected = dict(
            test=self.test_id, run_code=RunCode.DEBUG.value, tag=self.updated_tags
        )
        diffs = check_dict_items(expected, queue[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_unschedule_test(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_length = len(self.expected_account["queue"])

        unwrap(detect.unschedule)(
            detect, [dict(test_id=self.test_id, tags=self.updated_tags)]
        )
        self.expected_account["queue"] = [
            q for q in self.expected_account["queue"] if q["test"] != self.test_id
        ]
        queue = unwrap(iam_account.get_account)(iam_account)["queue"]
        assert queue_length - 1 == len(queue), json.dumps(queue, indent=2)

    def test_describe_activity(self, api, detect):
        res = requests.get(
            api,
            headers=dict(
                token=self.state["endpoint_token"],
                dos=f"darwin-x86_64",
                dat=f"{self.test_id}:100",
                version="2.7",
            ),
        )
        assert res.status_code in [200, 302]
        filters = dict(
            start=datetime.now(timezone.utc) - timedelta(days=1),
            finish=datetime.now(timezone.utc) + timedelta(days=1),
            endpoints=self.state["endpoint_id"],
            tests=self.test_id,
        )
        res = unwrap(detect.describe_activity)(detect, view="logs", filters=filters)
        assert 1 == len(res), json.dumps(res, indent=2)

        res = unwrap(detect.list_endpoints)(detect)
        assert 1 <= len(res)
        ep = [r for r in res if r["serial_num"] == self.serial][0]
        assert parse(ep["last_seen"]).date() == parse(ep["created"]).date()

    def test_delete_endpoint(self, detect):
        unwrap(detect.delete_endpoint)(detect, ident=self.state["endpoint_id"])
        res = unwrap(detect.list_endpoints)(detect)
        ep = [r for r in res if r["serial_num"] == self.serial]
        assert 0 == len(ep), json.dumps(ep, indent=2)

    def test_accept_terms(self, detect, iam_account, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        for user in self.expected_account["users"]:
            if user["handle"] == self.expected_account["whoami"]:
                if user["terms"].get("threat_intel", {}).get("1.0.0"):
                    with pytest.raises(Exception):
                        unwrap(detect.accept_terms)(
                            detect, name="threat_intel", version="1.0.0"
                        )
                    return

        unwrap(detect.accept_terms)(detect, name="threat_intel", version="1.0.0")
        res = unwrap(iam_account.get_account)(iam_account)

        for user in res["users"]:
            if user["handle"] == self.expected_account["whoami"]:
                assert user["terms"].get("threat_intel", {}).get("1.0.0"), json.dumps(
                    user, indent=2
                )
                assert parse(user["terms"]["threat_intel"]["1.0.0"]) <= datetime.now(
                    timezone.utc
                )
                break
