import logging
import os
import pytest

from prelude_sdk.models.codes import Control
from testutils import *


@pytest.mark.cleanup
@pytest.mark.order(-1)
class TestCleanUp:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.existing_account = request.getfixturevalue(
            "setup_existing_account"
        )

    def test_detach(self, iam_account, partner):
        res = unwrap(iam_account.get_account)(iam_account)
        controls = {c["instance_id"]: c["id"] for c in res["controls"]}
        if not controls:
            pytest.skip("No controls to detach")

        for i, c in controls.items():
            control = Control[c]
            logging.info(f"Detaching {control.name} with instance_id {i}")
            unwrap(partner.detach)(partner, partner=control, instance_id=i)
        res = unwrap(iam_account.get_account)(iam_account)
        assert not res["controls"]

    def test_delete_endpoint(self, detect):
        endpoints = unwrap(detect.list_endpoints)(detect)
        if not endpoints:
            pytest.skip("No endpoints to delete")

        for ep in endpoints:
            logging.info(
                f"Deleting endpoint {ep['host']}/{ep['serial_num']} ({ep['endpoint_id']})"
            )
            unwrap(detect.delete_endpoint)(detect, ident=ep["endpoint_id"])
        res = unwrap(detect.list_endpoints)(detect)
        assert not res

    def test_unschedule(self, detect, iam_account):
        if not self.existing_account["queue"]:
            pytest.skip("No tests in queue to unschedule")

        to_unschedule = []
        for item in self.existing_account["queue"]:
            if item["test"]:
                to_unschedule.append(dict(test_id=item["test"], tags=item["tag"] or ""))
            if item["threat"]:
                to_unschedule.append(
                    dict(threat_id=item["threat"], tags=item["tag"] or "")
                )

        logging.info(f"Unscheduling: {to_unschedule}")
        unwrap(detect.unschedule)(detect, to_unschedule)
        res = unwrap(iam_account.get_account)(iam_account)
        assert not res["queue"]

    def test_delete_threat_hunt(self, build, detect):
        threat_hunts = unwrap(detect.list_threat_hunts)(detect)
        mine = set(
            [
                r["id"]
                for r in threat_hunts
                if r["account_id"] == self.account.headers["account"]
            ]
        )
        if not mine:
            pytest.skip("No threat hunts to delete")
        for threat_hunt_id in mine:
            logging.info(f"Deleting threat hunt {threat_hunt_id}")
            unwrap(build.delete_threat_hunt)(build, threat_hunt_id=threat_hunt_id)
            with pytest.raises(Exception):
                unwrap(detect.get_threat_hunt)(detect, threat_hunt_id=threat_hunt_id)
        threat_hunts = unwrap(detect.list_threat_hunts)(detect)
        mine = [
            r["id"]
            for r in threat_hunts
            if r["account_id"] == self.account.headers["account"]
        ]
        assert not mine

    def test_delete_detection(self, build, detect):
        detections = unwrap(detect.list_detections)(detect)
        mine = set(
            [
                r["id"]
                for r in detections
                if r["account_id"] == self.account.headers["account"]
            ]
        )
        if not mine:
            pytest.skip("No detections to delete")
        for detection_id in mine:
            logging.info(f"Deleting detection {detection_id}")
            unwrap(build.delete_detection)(build, detection_id=detection_id)
            with pytest.raises(Exception):
                unwrap(detect.get_detection)(detect, detection_id=detection_id)
        detections = unwrap(detect.list_detections)(detect)
        mine = [
            r["id"]
            for r in detections
            if r["account_id"] == self.account.headers["account"]
        ]
        assert not mine

    def test_purge_threat(self, build, detect):
        threats = unwrap(detect.list_threats)(detect)
        mine = set(
            [
                r["id"]
                for r in threats
                if r["account_id"] == self.account.headers["account"]
            ]
        )
        if not mine:
            pytest.skip("No threats to purge")
        for threat_id in mine:
            logging.info(f"Purging threat {threat_id}")
            unwrap(build.delete_threat)(build, threat_id=threat_id, purge=True)
            with pytest.raises(Exception):
                unwrap(detect.get_threat)(detect, threat_id=threat_id)
        threats = unwrap(detect.list_threats)(detect)
        mine = [
            r["id"]
            for r in threats
            if r["account_id"] == self.account.headers["account"]
        ]
        assert not mine

    def test_purge_test(self, build, detect):
        tests = unwrap(detect.list_tests)(detect)
        mine = set(
            [
                r["id"]
                for r in tests
                if r["account_id"] == self.account.headers["account"]
            ]
        )
        if not mine:
            pytest.skip("No tests to purge")
        for test_id in mine:
            logging.info(f"Purging test {test_id}")
            unwrap(build.delete_test)(build, test_id=test_id, purge=True)
            with pytest.raises(Exception):
                unwrap(detect.get_test)(detect, test_id=test_id)
        tests = unwrap(detect.list_tests)(detect)
        mine = [
            r["id"] for r in tests if r["account_id"] == self.account.headers["account"]
        ]
        assert not mine

    def test_delete_service_user(self, iam_account):
        users = {u["handle"] for u in self.existing_account["token_users"]}
        if not users:
            pytest.skip("No service users to delete")
        for handle in users:
            logging.info(f"Deleting service user {handle}")
            unwrap(iam_account.delete_service_user)(iam_account, handle=handle)

        res = unwrap(iam_account.get_account)(iam_account)
        assert not res["token_users"]

    def test_purge_account(self, iam_account, purge_at_end):
        if not purge_at_end:
            pytest.skip("--purge_at_end is not set")
        unwrap(iam_account.purge_account)(iam_account)

    def test_purge_user(self, iam_user, purge_at_end):
        if not purge_at_end:
            pytest.skip("--purge_at_end is not set")
        unwrap(iam_user.purge_user)(iam_user)
