import json
import logging
import os
import pytest
import subprocess
from datetime import datetime, timedelta, timezone

from prelude_sdk.models.codes import RunCode
from testutils import *


@pytest.mark.stage4
@pytest.mark.order(12)
class TestProbe:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        cls.threat = request.getfixturevalue("my_threat")
        assert cls.threat, "No threat found for detect tests"
        cls.threat_id = cls.threat["id"]

        cls.host = "olive"
        cls.serial = "abc-123"
        cls.state = dict()

    def test_create_endpoint(self, detect, service_user_token):
        self.state["endpoint_token"] = detect.register_endpoint(
            host=self.host,
            serial_num=self.serial,
            reg_string=f"{self.expected_account['account_id']}/{service_user_token}",
        )

        res = unwrap(detect.list_endpoints)(detect)
        ep = [r for r in res if r["serial_num"] == self.serial]
        self.state["endpoint_id"] = ep[0]["endpoint_id"]

    def test_schedule(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_len = len(self.expected_account["queue"])
        unwrap(detect.schedule)(
            detect,
            [
                dict(
                    test_id="9f410a6b-76b6-45d6-b80f-d7365add057e",
                    run_code=RunCode.DEBUG.name,
                    tags="",
                ),
                dict(
                    test_id="b74ad239-2ddd-4b1e-b608-8397a43c7c54",
                    run_code=RunCode.RUN_ONCE.name,
                    tags="",
                ),
                # 3 tests in this threat (881.., b74..., 740... or uuid)
                dict(threat_id=self.threat_id, run_code=RunCode.DAILY.name, tags=""),
                # windows only test
                dict(
                    test_id="f12d00db-571f-4c51-a536-12a3577b5a4b",
                    run_code=RunCode.DEBUG.name,
                    tags="",
                ),
                # should not run
                dict(
                    test_id="8f9558f3-d451-46e3-bdda-97378c1e8ce4",
                    run_code=RunCode.DAILY.name,
                    tags="diff-tag",
                ),
            ],
        )

        queue = unwrap(iam_account.get_account)(iam_account)["queue"]
        self.expected_account["queue"] = queue
        assert queue_len + 5 == len(queue), json.dumps(queue, indent=2)

    def test_download_probe(self, probe):
        probe_name = "nocturnal"
        res = probe.download(name=probe_name, dos="darwin-arm64")
        assert res is not None

        with open(f"{probe_name}.sh", "w") as f:
            f.write(res)
        assert os.path.isfile(f"{probe_name}.sh")
        self.state["probe_file"] = os.path.abspath(f"{probe_name}.sh")
        os.chmod(self.state["probe_file"], 0o755)

    def test_describe_activity(self, detect):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        try:
            with pytest.raises(subprocess.TimeoutExpired):
                subprocess.run(
                    [self.state["probe_file"]],
                    capture_output=True,
                    env={"PRELUDE_TOKEN": self.state["endpoint_token"]},
                    timeout=120,
                )

            filters = dict(
                start=datetime.now(timezone.utc) - timedelta(days=1),
                finish=datetime.now(timezone.utc) + timedelta(days=1),
                endpoints=self.state["endpoint_id"],
            )
            res = unwrap(detect.describe_activity)(detect, view="logs", filters=filters)
            assert 6 <= len(res), json.dumps(res, indent=2)
            tests_run = {r["test"] for r in res}
            queued_tests = [
                "9f410a6b-76b6-45d6-b80f-d7365add057e",
                "b74ad239-2ddd-4b1e-b608-8397a43c7c54",
                "f12d00db-571f-4c51-a536-12a3577b5a4b",
            ] + self.threat["tests"]
            assert set(queued_tests) <= tests_run, json.dumps(tests_run, indent=2)
        finally:
            os.remove(self.state["probe_file"])

    def test_unschedule(self, detect, iam_account):
        if not self.expected_account["features"]["detect"]:
            pytest.skip("DETECT feature not enabled")

        queue_len = len(self.expected_account["queue"])
        unwrap(detect.unschedule)(
            detect,
            [
                dict(test_id="9f410a6b-76b6-45d6-b80f-d7365add057e", tags=""),
                dict(test_id="b74ad239-2ddd-4b1e-b608-8397a43c7c54", tags=""),
                dict(threat_id=self.threat_id, tags=""),
                dict(test_id="f12d00db-571f-4c51-a536-12a3577b5a4b", tags=""),
                dict(test_id="8f9558f3-d451-46e3-bdda-97378c1e8ce4", tags="diff-tag"),
            ],
        )

        queue = unwrap(iam_account.get_account)(iam_account)["queue"]
        self.expected_account["queue"] = queue
        assert queue_len - 5 == len(queue), json.dumps(queue, indent=2)

    def test_delete_endpoint(self, detect):
        unwrap(detect.delete_endpoint)(detect, ident=self.state["endpoint_id"])
        res = unwrap(detect.list_endpoints)(detect)
        ep = [r for r in res if r["serial_num"] == self.serial]
        assert 0 == len(ep), json.dumps(ep, indent=2)
