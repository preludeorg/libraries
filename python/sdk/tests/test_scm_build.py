import logging
import os
import pytest
import uuid

from prelude_sdk.models.codes import ControlCategory, PartnerEvents, RunCode
from testutils import *


@pytest.mark.stage1
@pytest.mark.order(9)
class TestScmBuild:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")

        cls.state = dict()
        cls.notification_id = str(uuid.uuid4())

    def test_create_object_exception(self, scm):
        res = unwrap(scm.create_object_exception)(
            scm,
            ControlCategory.ASSET_MANAGER,
            "hostname eq 'host1'",
            name="filter me",
            expires="5555-05-05",
        )
        assert res["exception_id"]
        self.state["exception_id"] = res["exception_id"]

    def test_update_object_exception(self, scm):
        res = unwrap(scm.update_object_exception)(
            scm,
            self.state["exception_id"],
            filter="hostname eq 'host2'",
            expires=None,
        )
        assert res["status"]

    def test_list_object_exceptions(self, scm):
        res = unwrap(scm.list_object_exceptions)(scm)
        exception = [x for x in res if x["id"] == self.state["exception_id"]]
        assert len(exception) == 1
        exception = exception[0]
        del exception["author"]
        del exception["created"]
        assert exception == {
            "category": ControlCategory.ASSET_MANAGER.value,
            "expires": None,
            "filter": "hostname eq 'host2'",
            "id": self.state["exception_id"],
            "name": "filter me",
        }

    def test_delete_object_exception(self, scm):
        res = unwrap(scm.delete_object_exception)(scm, self.state["exception_id"])
        assert res["status"]
        res = unwrap(scm.list_object_exceptions)(scm)
        assert not any(x["id"] == self.state["exception_id"] for x in res)

    def test_create_notification(self, scm):
        unwrap(scm.upsert_notification)(
            scm,
            ControlCategory.XDR,
            PartnerEvents.NO_EDR,
            RunCode.DAILY,
            0,
            ["test@email.com"],
            id=self.notification_id,
        )
        notifications = unwrap(scm.list_notifications)(scm)
        for notification in notifications:
            if notification["id"] == self.notification_id:
                assert notification["scheduled_hour"] == 0
                assert notification["event"] == PartnerEvents.NO_EDR.value

    def test_update_notification(self, scm):
        unwrap(scm.upsert_notification)(
            scm,
            ControlCategory.XDR,
            PartnerEvents.REDUCED_FUNCTIONALITY_MODE,
            RunCode.DAILY,
            1,
            ["test@email.com"],
            id=self.notification_id,
        )
        notifications = unwrap(scm.list_notifications)(scm)
        for notification in notifications:
            if notification["id"] == self.notification_id:
                assert notification["scheduled_hour"] == 1
                assert (
                    notification["event"]
                    == PartnerEvents.REDUCED_FUNCTIONALITY_MODE.value
                )

    def test_delete_notification(self, scm):
        unwrap(scm.delete_notification)(scm, self.notification_id)
        notifications = unwrap(scm.list_notifications)(scm)
        for notification in notifications:
            assert notification["id"] != self.notification_id
