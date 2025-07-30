import logging
import os
import pytest
import requests
import time


from prelude_sdk.models.codes import Control, ControlCategory, SCMCategory
from testutils import *


@pytest.mark.stage3
@pytest.mark.order(10)
class TestScmAcrossControls:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        if not cls.expected_account["controls"]:
            pytest.skip("Partners not attached")

    def test_evaluation_summary(self, scm):
        summary = unwrap(scm.evaluation_summary)(scm)
        assert summary.keys() == {"endpoint_summary", "user_summary", "inbox_summary"}
        for key in summary:
            assert "error" not in summary[key]

    def test_technique_summary(self, scm):
        summary = unwrap(scm.technique_summary)(scm, "T1078,T1027")
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

    def test_export_endpoints_csv(self, export, jobs):
        job_id = unwrap(export.export_scm)(
            export,
            SCMCategory.ENDPOINT,
            filter="contains(hostname, 'spencer')",
            top=1,
        )["job_id"]
        while (result := unwrap(jobs.job_status)(jobs, job_id))["end_time"] is None:
            time.sleep(3)
        assert result["successful"], result
        csv = requests.get(result["results"]["url"], timeout=10).content.decode("utf-8")
        assert len(csv.strip("\r\n").split("\r\n")) == 2


@pytest.mark.stage3
@pytest.mark.order(11)
class ScmPerControl:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not self.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")

        controls = {c["id"]: c["instance_id"] for c in cls.expected_account["controls"]}
        if cls.control.value not in controls:
            pytest.skip(f"{cls.control.name} not attached")
        cls.instance_id = controls[cls.control.value]

    def test_update_evaluation(self, jobs, scm):
        try:
            job_id = unwrap(scm.update_evaluation)(scm, self.control, self.instance_id)[
                "job_id"
            ]
            while (result := unwrap(jobs.job_status)(jobs, job_id))["end_time"] is None:
                time.sleep(3)
            assert result["successful"]
        except Exception as e:
            if "job is already running" in str(e):
                pytest.skip(
                    "Skipping due to existing job initiated from partner attach"
                )
            else:
                raise e

    def test_evaluation(self, scm):
        evaluation = unwrap(scm.evaluation)(scm, self.control, self.instance_id)
        if "endpoint_evaluation" in evaluation:
            evaluation = evaluation["endpoint_evaluation"]
            assert {"policies"} == evaluation.keys()
            if self.control.control_category == ControlCategory.XDR:
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


for control in Control:
    if control.scm_category != SCMCategory.NONE:
        cls = type(
            f"TestScmPerControl_{control.name}",
            (ScmPerControl,),
            dict(
                control=control,
                partner_api=os.getenv(f"{control.name.upper()}_API") or "",
                user=os.getenv(f"{control.name.upper()}_USER") or "",
                secret=os.getenv(f"{control.name.upper()}_SECRET") or "",
            ),
        )
        globals()[cls.__name__] = cls


@pytest.mark.stage3
@pytest.mark.order(11)
class TestScmGroups:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        cls.controls = {
            c["id"]: c["instance_id"] for c in cls.expected_account["controls"]
        }

    def test_groups(self, partner, scm, jobs):
        control = Control.ENTRA
        if control.value not in self.controls:
            pytest.skip(f"{control.name} not attached")

        instance_id = self.controls.get(control.value)
        groups = unwrap(partner.partner_groups)(
            partner, partner=control, instance_id=instance_id
        )
        assert len(groups) > 0, "No groups found for the partner"
        group_id = "3af0324e-0cbe-491c-8d1b-98dba25ad500"
        assert group_id in [g["id"] for g in groups]

        job_id = unwrap(scm.update_partner_groups)(
            scm,
            partner=control,
            instance_id=instance_id,
            group_ids=[group_id],
        )["job_id"]
        while (result := unwrap(jobs.job_status)(jobs, job_id))["end_time"] is None:
            time.sleep(3)
        assert result["successful"]

        groups = unwrap(scm.list_partner_groups)(scm)
        actual = [dict(control=g["control"], group_id=g["group_id"]) for g in groups]
        expected = dict(control=control.value, group_id=group_id)
        assert expected in actual
