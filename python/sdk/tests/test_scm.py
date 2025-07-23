import pytest
import requests
import time
import uuid

from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.partner_controller import PartnerController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import (
    Control,
    ControlCategory,
    PartnerEvents,
    RunCode,
    SCMCategory,
)


@pytest.mark.order(8)
@pytest.mark.usefixtures("setup_account")
class TestScmAcrossControls:
    def setup_class(self):
        if not pytest.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        if not pytest.controls:
            pytest.skip("Partners not attached")
        self.export = ExportController(pytest.account)
        self.jobs = JobsController(pytest.account)
        self.scm = ScmController(pytest.account)
        self.notification_id = str(uuid.uuid4())

    def test_create_notification(self, unwrap):
        unwrap(self.scm.upsert_notification)(
            self.scm,
            ControlCategory.XDR,
            PartnerEvents.NO_EDR,
            RunCode.DAILY,
            0,
            ["test@email.com"],
            id=self.notification_id,
        )
        notifications = unwrap(self.scm.list_notifications)(self.scm)
        for notification in notifications:
            if notification["id"] == self.notification_id:
                assert notification["scheduled_hour"] == 0
                assert notification["event"] == PartnerEvents.NO_EDR.value

    def test_update_notification(self, unwrap):
        unwrap(self.scm.upsert_notification)(
            self.scm,
            ControlCategory.XDR,
            PartnerEvents.REDUCED_FUNCTIONALITY_MODE,
            RunCode.DAILY,
            1,
            ["test@email.com"],
            id=self.notification_id,
        )
        notifications = unwrap(self.scm.list_notifications)(self.scm)
        for notification in notifications:
            if notification["id"] == self.notification_id:
                assert notification["scheduled_hour"] == 1
                assert (
                    notification["event"]
                    == PartnerEvents.REDUCED_FUNCTIONALITY_MODE.value
                )

    def test_delete_notification(self, unwrap):
        unwrap(self.scm.delete_notification)(self.scm, self.notification_id)
        notifications = unwrap(self.scm.list_notifications)(self.scm)
        for notification in notifications:
            assert notification["id"] != self.notification_id

    def test_evaluation_summary(self, unwrap):
        def _compare_keys(expected, actual):
            assert set(expected.keys()) == set(
                actual.keys()
            ), f"Keys are not the same {expected.keys()} {actual.keys()}"
            for key in expected.keys():
                if isinstance(expected[key], list) and isinstance(actual[key], list):
                    nested_expected = expected[key][0]
                    if not actual[key]:
                        continue
                    nested_actual = actual[key][0]
                elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
                    nested_expected = expected[key]
                    nested_actual = actual[key]
                else:
                    continue
                _compare_keys(nested_expected, nested_actual)

        summary = unwrap(self.scm.evaluation_summary)(self.scm)
        assert summary.keys() == {
            "endpoint_summary",
            "user_summary",
            "inbox_summary",
        }

    def test_technique_summary(self, unwrap):
        summary = unwrap(self.scm.technique_summary)(self.scm, "T1078,T1027")
        assert len(summary) > 0
        assert {"instances", "technique"} == summary[0].keys()
        assert len(summary[0]["instances"]) > 0
        assert {
            "control",
            "excepted",
            "instance_id",
            "setting_count",
            "setting_misconfiguration_count",
        } == summary[0]["instances"][0].keys()
        assert {"setting_count", "setting_misconfiguration_count"} == summary[0][
            "instances"
        ][0]["excepted"].keys()

    def test_export_endpoints_csv(self, unwrap):
        job_id = unwrap(self.export.export_scm)(
            self.export,
            SCMCategory.ENDPOINT,
            filter="contains(hostname, 'spencer')",
            top=1,
        )["job_id"]
        while (result := unwrap(self.jobs.job_status)(self.jobs, job_id))[
            "end_time"
        ] is None:
            time.sleep(3)
        assert result["successful"], result
        csv = requests.get(result["results"]["url"], timeout=10).content.decode("utf-8")
        assert len(csv.strip("\r\n").split("\r\n")) == 2


@pytest.mark.order(9)
@pytest.mark.usefixtures("setup_account")
@pytest.mark.parametrize(
    "control", [c for c in Control if c.scm_category != SCMCategory.NONE]
)
class TestScmPerControl:
    def setup_class(self):
        if not pytest.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        self.jobs = JobsController(pytest.account)
        self.partner = PartnerController(pytest.account)
        self.scm = ScmController(pytest.account)

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self, control):
        if control.value not in pytest.controls:
            pytest.skip(f"{control.name} not attached")
        yield

    def test_update_evaluation(self, unwrap, control):
        instance_id = pytest.controls.get(control.value)
        assert instance_id
        try:
            job_id = unwrap(self.scm.update_evaluation)(self.scm, control, instance_id)[
                "job_id"
            ]
            while (result := unwrap(self.jobs.job_status)(self.jobs, job_id))[
                "end_time"
            ] is None:
                time.sleep(3)
            assert result["successful"]
        except Exception as e:
            if "job is already running" in str(e):
                pytest.skip(
                    "Skipping due to existing job initiated from partner attach"
                )
            else:
                raise e

    def test_evaluation(self, unwrap, control):
        instance_id = pytest.controls.get(control.value)
        assert instance_id
        evaluation = unwrap(self.scm.evaluation)(self.scm, control, instance_id)
        if "endpoint_evaluation" in evaluation:
            evaluation = evaluation["endpoint_evaluation"]
            assert {"policies"} == evaluation.keys()
            if control.control_category == ControlCategory.XDR:
                assert len(evaluation["policies"]) > 0
                assert {
                    "id",
                    "name",
                    "platform",
                    "settings",
                    "conflict_count",
                    "endpoint_count",
                    "success_count",
                } == evaluation["policies"][0].keys()
            else:
                assert len(evaluation["policies"]) == 0
        elif "user_evaluation" in evaluation:
            evaluation = evaluation["user_evaluation"]
            assert {"policies"} == evaluation.keys()
            assert len(evaluation["policies"]) > 0
            assert {
                "id",
                "name",
                "noncompliant_hostnames",
                "settings",
                "user_count",
            } == evaluation["policies"][0].keys()
        elif "inbox_evaluation" in evaluation:
            evaluation = evaluation["inbox_evaluation"]
            assert {"policies"} == evaluation.keys()
            assert len(evaluation["policies"]) > 0
            assert {"id", "name", "settings", "inbox_count"} == evaluation["policies"][
                0
            ].keys()
        else:
            assert False, "No evaluation returned"


@pytest.mark.order(9)
@pytest.mark.usefixtures("setup_account")
class TestScmGroups:
    def setup_class(self):
        if not pytest.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        self.jobs = JobsController(pytest.account)
        self.partner = PartnerController(pytest.account)
        self.scm = ScmController(pytest.account)

    def test_groups(self, unwrap):
        control = Control.ENTRA
        if control.value not in pytest.controls:
            pytest.skip(f"{control.name} not attached")

        instance_id = pytest.controls.get(control.value)
        groups = unwrap(self.partner.partner_groups)(
            self.partner, partner=control, instance_id=instance_id
        )
        assert len(groups) > 0, "No groups found for the partner"
        group_id = "3af0324e-0cbe-491c-8d1b-98dba25ad500"
        assert group_id in [g["id"] for g in groups]

        job_id = unwrap(self.scm.update_partner_groups)(
            self.scm,
            partner=control,
            instance_id=instance_id,
            group_ids=[group_id],
        )["job_id"]
        while (result := unwrap(self.jobs.job_status)(self.jobs, job_id))[
            "end_time"
        ] is None:
            time.sleep(3)
        assert result["successful"]

        groups = unwrap(self.scm.list_partner_groups)(self.scm)
        actual = [dict(control=g["control"], group_id=g["group_id"]) for g in groups]
        expected = dict(control=control.value, group_id=group_id)
        assert expected in actual
