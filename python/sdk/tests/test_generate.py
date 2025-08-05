import logging
import os
import pytest
import time

from prelude_sdk.models.codes import Control
from testutils import *


@pytest.mark.stage4
@pytest.mark.order(13)
class TestGenerate:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        cls.threat_intel_pdf = (
            os.path.dirname(os.path.realpath(__file__)) + "/data/threat_intel.pdf"
        )
        cls.state = dict()

    def test_upload_threat_intel(self, detect, generate):
        try:
            unwrap(detect.accept_terms)(detect, name="threat_intel", version="1.0.0")
        except Exception as e:
            pass

        res = unwrap(generate.upload_threat_intel)(generate, file=self.threat_intel_pdf)
        job_id = res["job_id"]
        assert check_if_string_is_uuid(job_id)

        while True:
            time.sleep(5)
            res = unwrap(generate.get_threat_intel)(generate, job_id=job_id)
            match status := res.get("status"):
                case "RUNNING":
                    if res["step"] == "GENERATE":
                        assert 2 == res["num_tasks"], json.dumps(res)
                case "COMPLETE":
                    assert 14 == len(res["output"]), json.dumps(res)
                    for output in res["output"]:
                        assert {"status", "technique"} < set(output.keys()), json.dumps(
                            output
                        )
                        assert (
                            "ai_generated" in output
                            or "existing_test" in output
                            or "excluded" in output
                        ), json.dumps(output)
                    return
                case "FAILED":
                    assert False, f"threat_gen FAILED: {json.dumps(res)}"
                case _:
                    assert (
                        False
                    ), f" Unexpected status: {status}\n Response: {json.dumps(res)}"

    def test_list_advisories(self, partner):
        if not self.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        res = unwrap(partner.list_advisories)(
            partner, partner=Control.CROWDSTRIKE, limit=5, offset=0
        )
        assert 1 <= len(res["advisories"])
        assert res["advisories"][0]["id"]
        assert {"created", "description", "id", "name", "tags", "slug"} == set(
            res["advisories"][0].keys()
        )
        assert res["pagination"]["limit"] == 5
        assert res["pagination"]["offset"] == 0
        assert res["pagination"]["total"] > 0
        self.state["crowdstrike_advisory_id"] = res["advisories"][0]["id"]

    def test_generate_from_partner_advisory(self, generate):
        partners = [p["id"] for p in self.expected_account["controls"]]
        if Control.CROWDSTRIKE.value not in partners:
            pytest.skip("CROWDSTRIKE not attached")

        res = unwrap(generate.generate_from_partner_advisory)(
            generate,
            partner=Control.CROWDSTRIKE,
            advisory_id=self.state["crowdstrike_advisory_id"],
        )
        job_id = res["job_id"]
        assert check_if_string_is_uuid(job_id)

        while True:
            time.sleep(5)
            res = unwrap(generate.get_threat_intel)(generate, job_id=job_id)
            match res.get("status"):
                case "COMPLETE":
                    for output in res["output"]:
                        assert {"status", "technique"} < set(output.keys()), json.dumps(
                            output
                        )
                        assert (
                            "ai_generated" in output
                            or "existing_test" in output
                            or "excluded" in output
                        ), json.dumps(output)
                    return
