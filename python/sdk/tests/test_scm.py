import pytest
import requests
import time
import uuid

from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.jobs_controller import JobsController
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
        expected = {
            "inbox_summary": {
                "categories": [
                    {
                        "category": None,
                        "inbox_count": None,
                        "excepted": {
                            "inbox_count": None,
                        },
                        "instances": [
                            {
                                "control": None,
                                "inbox_count": None,
                                "instance_id": None,
                                "setting_count": None,
                                "setting_misconfiguration_count": None,
                                "excepted": {
                                    "inbox_count": None,
                                    "setting_misconfiguration_count": None,
                                },
                            }
                        ],
                    }
                ],
                "inbox_count": None,
                "excepted": {
                    "inbox_count": None,
                },
            },
            "user_summary": {
                "categories": [
                    {
                        "category": None,
                        "control_failure_count": None,
                        "any_endpoint_failure_count": None,
                        "all_endpoint_failure_count": None,
                        "user_count": None,
                        "excepted": {
                            "control_failure_count": None,
                            "any_endpoint_failure_count": None,
                            "all_endpoint_failure_count": None,
                            "user_count": None,
                        },
                        "instances": [
                            {
                                "control": None,
                                "instance_id": None,
                                "control_failure_count": None,
                                "missing_mfa_count": None,
                                "user_count": None,
                                "missing_asset_manager_count": None,
                                "missing_edr_count": None,
                                "missing_vuln_manager_count": None,
                                "any_endpoint_failure_count": None,
                                "all_endpoint_failure_count": None,
                                "setting_count": None,
                                "setting_misconfiguration_count": None,
                                "excepted": {
                                    "control_failure_count": None,
                                    "missing_mfa_count": None,
                                    "user_count": None,
                                    "missing_asset_manager_count": None,
                                    "missing_edr_count": None,
                                    "missing_vuln_manager_count": None,
                                    "any_endpoint_failure_count": None,
                                    "all_endpoint_failure_count": None,
                                    "setting_misconfiguration_count": None,
                                },
                            },
                        ],
                    }
                ],
                "user_count": None,
                "control_failure_count": None,
                "any_endpoint_failure_count": None,
                "all_endpoint_failure_count": None,
                "excepted": {
                    "user_count": None,
                    "control_failure_count": None,
                    "any_endpoint_failure_count": None,
                    "all_endpoint_failure_count": None,
                },
            },
            "endpoint_summary": {
                "categories": [
                    {
                        "category": None,
                        "control_failure_count": None,
                        "endpoint_count": None,
                        "missing_asset_manager_count": None,
                        "missing_edr_count": None,
                        "missing_vuln_manager_count": None,
                        "missing_vuln_scan_count": None,
                        "excepted": {
                            "control_failure_count": None,
                            "endpoint_count": None,
                            "missing_asset_manager_count": None,
                            "missing_edr_count": None,
                            "missing_vuln_manager_count": None,
                            "missing_vuln_scan_count": None,
                        },
                        "instances": [
                            {
                                "control": None,
                                "instance_id": None,
                                "control_failure_count": None,
                                "endpoint_count": None,
                                "no_av_policy": None,
                                "no_edr_policy": None,
                                "policy_conflict_count": None,
                                "reduced_functionality_mode": None,
                                "missing_agent_count": None,
                                "missing_scan_count": None,
                                "out_of_date_scan_count": None,
                                "setting_count": None,
                                "setting_misconfiguration_count": None,
                                "excepted": {
                                    "control_failure_count": None,
                                    "endpoint_count": None,
                                    "no_av_policy": None,
                                    "no_edr_policy": None,
                                    "reduced_functionality_mode": None,
                                    "missing_agent_count": None,
                                    "missing_scan_count": None,
                                    "out_of_date_scan_count": None,
                                    "setting_misconfiguration_count": None,
                                },
                            }
                        ],
                    },
                ],
                "endpoint_count": None,
                "missing_asset_manager_count": None,
                "missing_edr_count": None,
                "missing_vuln_manager_count": None,
                "missing_vuln_scan_count": None,
                "excepted": {
                    "endpoint_count": None,
                    "missing_asset_manager_count": None,
                    "missing_edr_count": None,
                    "missing_vuln_manager_count": None,
                    "missing_vuln_scan_count": None,
                },
            },
        }

        _compare_keys(expected, summary)

    def test_technique_summary(self, unwrap):
        summary = unwrap(self.scm.technique_summary)(self.scm, "T1078,T1027")
        assert len(summary) > 0
        assert {"instances", "technique"} == summary[0].keys()
        assert len(summary[0]["instances"]) > 0
        assert {
            "control",
            "instance_id",
            "setting_count",
            "setting_misconfiguration_count",
        } == summary[0]["instances"][0].keys()

    def test_export_endpoints_csv(self, unwrap):
        job_id = unwrap(self.export.export_scm)(
            self.export,
            SCMCategory.ENDPOINT,
            filter="contains(normalized_hostname, 'spencer')",
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
        self.scm = ScmController(pytest.account)
        self.jobs = JobsController(pytest.account)

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
