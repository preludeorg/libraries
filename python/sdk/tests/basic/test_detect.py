import json
import pytest
import requests
from datetime import datetime, timedelta, timezone

from dateutil.parser import parse

from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.iam_controller import IAMAccountController

from testutils import *


@pytest.mark.order(6)
@pytest.mark.usefixtures("setup_account", "setup_test", "setup_threat")
class TestDetect:

    def setup_class(self):
        self.iam = IAMAccountController(pytest.account)
        self.detect = DetectController(pytest.account)

        self.host = "test_host"
        self.serial = "test_serial"
        self.tags = "alpha"
        self.updated_tags = "beta"

    def test_list_techniques(self):
        res = unwrap(self.detect.list_techniques)(self.detect)
        assert 1 <= len(res)
        assert {
            "category",
            "description",
            "expected",
            "id",
            "name",
            "relevant_categories",
        } == set(res[0].keys())

    def test_register_endpoint(self):
        res = self.detect.register_endpoint(
            host=self.host,
            serial_num=self.serial,
            reg_string=f"{pytest.expected_account['account_id']}/{pytest.service_user_token}",
            tags=self.tags,
        )
        assert 32 == len(res)

        pytest.token = res
        pytest.expected_endpoint = dict(
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

    def test_list_endpoints(self):
        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert 1 <= len(res)
        ep = [r for r in res if r["serial_num"] == self.serial][0]
        pytest.expected_endpoint["endpoint_id"] = ep["endpoint_id"]
        pytest.endpoint_id = ep["endpoint_id"]

        diffs = check_dict_items(pytest.expected_endpoint, ep)
        assert not diffs, json.dumps(diffs, indent=2)
        assert ep["last_seen"] is None

    def test_update_endpoint(self):
        res = unwrap(self.detect.update_endpoint)(
            self.detect, endpoint_id=pytest.endpoint_id, tags=self.updated_tags
        )
        assert res["id"] == pytest.endpoint_id
        pytest.expected_endpoint["tags"] = [self.updated_tags]

        res = unwrap(self.detect.list_endpoints)(self.detect)
        ep = [r for r in res if r["endpoint_id"] == pytest.endpoint_id][0]
        diffs = check_dict_items(pytest.expected_endpoint, ep)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_describe_activity(self, api):
        res = requests.get(
            api,
            headers=dict(
                token=pytest.token,
                dos=f"darwin-x86_64",
                dat=f"{pytest.test_id}:100",
                version="2.7",
            ),
        )
        assert res.status_code in [200, 302]
        filters = dict(
            start=datetime.now(timezone.utc) - timedelta(days=1),
            finish=datetime.now(timezone.utc) + timedelta(days=1),
            endpoints=pytest.endpoint_id,
            tests=pytest.test_id,
        )
        res = unwrap(self.detect.describe_activity)(
            self.detect, view="logs", filters=filters
        )
        assert 1 == len(res), json.dumps(res, indent=2)

        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert 1 <= len(res)
        ep = [r for r in res if r["serial_num"] == self.serial][0]
        assert parse(ep["last_seen"]).date() == parse(ep["created"]).date()

    def test_delete_endpoint(self):
        unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_id)
        res = unwrap(self.detect.list_endpoints)(self.detect)
        ep = [r for r in res if r["serial_num"] == self.serial]
        assert 0 == len(ep), json.dumps(ep, indent=2)

    def test_accept_terms(self, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        for user in pytest.expected_account["users"]:
            if user["handle"] == pytest.expected_account["whoami"]:
                if user["terms"].get("threat_intel", {}).get("1.0.0"):
                    with pytest.raises(Exception):
                        unwrap(self.detect.accept_terms)(
                            self.detect, name="threat_intel", version="1.0.0"
                        )
                    return

        unwrap(self.detect.accept_terms)(
            self.detect, name="threat_intel", version="1.0.0"
        )
        res = unwrap(self.iam.get_account)(self.iam)

        for user in res["users"]:
            if user["handle"] == pytest.expected_account["whoami"]:
                assert user["terms"].get("threat_intel", {}).get("1.0.0"), json.dumps(
                    user, indent=2
                )
                assert parse(user["terms"]["threat_intel"]["1.0.0"]) <= datetime.now(
                    timezone.utc
                )
                break
