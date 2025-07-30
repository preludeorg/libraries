import json
import logging
import os
import pytest
import templates
import time
from datetime import datetime, timedelta, timezone
from importlib.resources import files

from dateutil.parser import parse

from prelude_sdk.models.codes import Control, EDRResponse
from testutils import *


@pytest.mark.stage1
@pytest.mark.order(3)
class TestVST:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        cls.test_id = str(uuid.uuid4())
        cls.state = dict()

    def test_create_test(self, build):
        self.state["expected_test"] = unwrap(build.create_test)(
            build, test_id=self.test_id, name="test_name", unit="custom", technique=None
        )

        expected = dict(
            account_id=self.account.headers["account"],
            attachments=[],
            author=self.expected_account["whoami"]["handle"],
            expected=dict(crowdstrike=1),
            id=self.test_id,
            intel_context=None,
            name="test_name",
            supported_platforms=[],
            technique=None,
            tombstoned=None,
            unit="custom",
        )

        diffs = check_dict_items(expected, self.state["expected_test"])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_upload(self, build):
        def wait_for_compile(job_id):
            timeout = time.time() + 120
            while time.time() < timeout:
                time.sleep(5)
                res = unwrap(build.get_compile_status)(build, job_id=job_id)
                if res["status"] != "RUNNING":
                    break
            return res

        template = files(templates).joinpath("template.go").read_text()
        res = unwrap(build.upload)(
            build,
            test_id=self.test_id,
            filename=f"{self.test_id}.go",
            data=template.encode("utf-8"),
        )
        self.state["expected_test"]["attachments"].append(res["filename"])
        for suffix in [
            "darwin-arm64",
            "darwin-x86_64",
            "linux-arm64",
            "linux-x86_64",
            "windows-x86_64",
        ]:
            self.state["expected_test"]["attachments"].append(
                f"{self.test_id}_{suffix}"
            )
        self.state["expected_test"]["supported_platforms"] = [
            "darwin",
            "linux",
            "windows",
        ]

        expected = dict(
            compile_job_id=res["compile_job_id"],
            filename=f"{self.test_id}.go",
            id=self.test_id,
        )
        assert expected == res

        assert res.get("compile_job_id") is not None
        res = wait_for_compile(res["compile_job_id"])
        per_platform_res = res["results"]
        assert "COMPLETE" == res["status"]
        assert 5 == len(per_platform_res)
        for platform in per_platform_res:
            assert "SUCCEEDED" == platform["status"]

    def test_compile_code_string(self, build):
        def wait_for_compile(job_id):
            timeout = time.time() + 60
            while time.time() < timeout:
                time.sleep(5)
                res = unwrap(build.get_compile_status)(build, job_id=job_id)
                if res["status"] != "RUNNING":
                    break
            return res

        res = unwrap(build.compile_code_string)(
            build, code="package main\n\nfunc main() {}"
        )
        assert res["job_id"] is not None
        res = wait_for_compile(res["job_id"])
        assert "COMPLETE" == res["status"]
        assert 5 == len(res["results"])
        for platform in res["results"]:
            assert "SUCCEEDED" == platform["status"]

    def test_get_test(self, detect):
        res = unwrap(detect.get_test)(detect, test_id=self.test_id)

        diffs = check_dict_items(self.state["expected_test"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_tests(self, detect):
        res = unwrap(detect.list_tests)(detect)
        owners = set([r["account_id"] for r in res])
        assert {"prelude", self.account.headers["account"]} >= owners

        mine = [r for r in res if r["id"] == self.state["expected_test"]["id"]]
        assert 1 == len(mine)
        del self.state["expected_test"]["attachments"]
        diffs = check_dict_items(
            self.state["expected_test"] | dict(detection_platforms=[]), mine[0]
        )
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_test(self, build):
        updated_name = "updated_test"
        res = unwrap(build.update_test)(
            build,
            crowdstrike_expected_outcome=EDRResponse.PREVENT,
            name=updated_name,
            technique="T1234.001",
            test_id=self.test_id,
        )

        self.state["expected_test"]["expected"][
            "crowdstrike"
        ] = EDRResponse.PREVENT.value
        self.state["expected_test"]["name"] = updated_name
        self.state["expected_test"]["technique"] = "T1234.001"

        diffs = check_dict_items(self.state["expected_test"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_download(self, detect):
        filename = f"{self.test_id}.go"
        res = unwrap(detect.download)(detect, test_id=self.test_id, filename=filename)
        assert res is not None
        with open(filename, "wb") as f:
            f.write(res)
        assert os.path.isfile(filename)
        os.remove(filename)

    def test_tombstone_test(self, build, detect):
        unwrap(build.delete_test)(build, test_id=self.test_id, purge=False)
        res = unwrap(detect.get_test)(detect, test_id=self.test_id)
        self.state["expected_test"]["tombstoned"] = res["tombstoned"]

        diffs = check_dict_items(self.state["expected_test"], res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res["tombstoned"]).replace(tzinfo=timezone.utc) <= datetime.now(
            timezone.utc
        ) + timedelta(minutes=1)

    def test_undelete_test(self, build, detect):
        unwrap(build.undelete_test)(build, test_id=self.test_id)
        res = unwrap(detect.get_test)(detect, test_id=self.test_id)
        self.state["expected_test"]["tombstoned"] = None

        diffs = check_dict_items(self.state["expected_test"], res)
        assert not diffs, json.dumps(diffs, indent=2)


@pytest.mark.stage2
@pytest.mark.order(4)
class TestThreat:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        cls.test_id = request.getfixturevalue("my_test_id")
        assert cls.test_id, "No test found for threat creation"

        cls.threat_id = str(uuid.uuid4())
        cls.state = dict()

    def test_create_threat(self, build):
        tests = [
            "881f9052-fb52-4daf-9ad2-0a7ad9615baf",
            "b74ad239-2ddd-4b1e-b608-8397a43c7c54",
            self.test_id,
        ]
        self.state["expected_threat"] = unwrap(build.create_threat)(
            build,
            name="threat_name",
            published="2023-11-13",
            threat_id=self.threat_id,
            source_id="aa23-061a",
            source="https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a",
            tests=",".join(tests),
        )

        expected = dict(
            account_id=self.account.headers["account"],
            author=self.expected_account["whoami"]["handle"],
            id=self.threat_id,
            name="threat_name",
            published="2023-11-13",
            source="https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a",
            source_id="aa23-061a",
            tests=tests,
            techniques=["T1204.002", "T1234.001", "T1486"],
            tombstoned=None,
        )

        diffs = check_dict_items(expected, self.state["expected_threat"])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_threat(self, detect):
        res = unwrap(detect.get_threat)(detect, threat_id=self.threat_id)

        diffs = check_dict_items(self.state["expected_threat"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threats(self, detect):
        res = unwrap(detect.list_threats)(detect)
        owners = set([r["account_id"] for r in res])
        assert {"prelude", self.account.headers["account"]} >= owners

        mine = [r for r in res if r["id"] == self.state["expected_threat"]["id"]]
        assert 1 == len(mine)
        diffs = check_dict_items(self.state["expected_threat"], mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_threat(self, build):
        updated_name = "updated-threat"
        updated_tests = [
            "881f9052-fb52-4daf-9ad2-0a7ad9615baf",
            "74077d3b-6a2f-49fa-903e-99cad6f34cf6",
            "b74ad239-2ddd-4b1e-b608-8397a43c7c54",
        ]
        res = unwrap(build.update_threat)(
            build,
            threat_id=self.threat_id,
            name=updated_name,
            source="",
            tests=",".join(updated_tests),
        )

        self.state["expected_threat"]["name"] = updated_name
        self.state["expected_threat"]["source"] = None
        self.state["expected_threat"]["tests"] = updated_tests
        self.state["expected_threat"]["techniques"] = [
            "T1204.002",
            "T1204.002",
            "T1486",
        ]

        diffs = check_dict_items(self.state["expected_threat"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_tombstone_threat(self, build, detect):
        unwrap(build.delete_threat)(build, threat_id=self.threat_id, purge=False)
        res = unwrap(detect.get_threat)(detect, threat_id=self.threat_id)
        self.state["expected_threat"]["tombstoned"] = res["tombstoned"]

        diffs = check_dict_items(self.state["expected_threat"], res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res["tombstoned"]).replace(tzinfo=timezone.utc) <= datetime.now(
            timezone.utc
        ) + timedelta(minutes=1)

    def test_undelete_threat(self, build, detect):
        unwrap(build.undelete_threat)(build, threat_id=self.threat_id)
        res = unwrap(detect.get_threat)(detect, threat_id=self.threat_id)
        self.state["expected_threat"]["tombstoned"] = None

        diffs = check_dict_items(self.state["expected_threat"], res)
        assert not diffs, json.dumps(diffs, indent=2)


@pytest.mark.stage2
@pytest.mark.order(5)
class TestDetection:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["detections"]:
            pytest.skip("DETECTIONS feature not enabled")

        cls.test_id = request.getfixturevalue("my_test_id")
        assert cls.test_id, "No test found for detection creation"
        cls.detection_id = str(uuid.uuid4())
        cls.detection_rule = """
        title: Suspicious Command Line Usage in Windows
        description: Detects suspicious use of cmd.exe or powershell.exe with commands often used for reconnaissance like directory listing, tree viewing, or searching for sensitive files.
        logsource:
            category: process_creation
            product: windows
        detection:
            selection:
                ParentImage: 'cmd.exe'
            condition: selection
        level: medium
        """
        cls.state = dict()

    def test_create_detection(self, build):
        self.state["expected_detection"] = unwrap(build.create_detection)(
            build,
            rule=self.detection_rule,
            test_id=self.test_id,
            detection_id=self.detection_id,
            rule_id=str(uuid.uuid4()),
        )
        expected = dict(
            account_id=self.account.headers["account"],
            id=self.detection_id,
            name="Suspicious Command Line Usage in Windows",
            rule=dict(
                title="Suspicious Command Line Usage in Windows",
                description="Detects suspicious use of cmd.exe or powershell.exe with commands often used for reconnaissance like directory listing, tree viewing, or searching for sensitive files.",
                logsource=dict(category="process_creation", product="windows"),
                detection=dict(
                    condition="selection", selection=dict(ParentImage="cmd.exe")
                ),
                level="medium",
            ),
            rule_id=self.state["expected_detection"]["rule_id"],
            test=self.test_id,
        )

        diffs = check_dict_items(expected, self.state["expected_detection"])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_detection(self, detect):
        res = unwrap(detect.get_detection)(detect, detection_id=self.detection_id)

        diffs = check_dict_items(self.state["expected_detection"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_detections(self, detect):
        res = unwrap(detect.list_detections)(detect)
        owners = set([r["account_id"] for r in res])
        assert {"prelude", self.account.headers["account"]} >= owners

        mine = [r for r in res if r["id"] == self.state["expected_detection"]["id"]]
        assert 1 == len(mine)
        diffs = check_dict_items(self.state["expected_detection"], mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_detection(self, build):
        updated_rule = self.detection_rule.replace(
            self.state["expected_detection"]["rule"]["title"], "Suspicious no more"
        )
        res = unwrap(build.update_detection)(
            build, detection_id=self.detection_id, rule=updated_rule
        )
        self.state["expected_detection"]["rule"]["title"] = "Suspicious no more"

        diffs = check_dict_items(self.state["expected_detection"], res)
        assert not diffs, json.dumps(diffs, indent=2)


@pytest.mark.stage2
@pytest.mark.order(6)
class TestThreatHunt:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )
        if not cls.expected_account["features"]["threat_intel"]:
            pytest.skip("THREAT_INTEL feature not enabled")

        cls.test_id = request.getfixturevalue("my_test_id")
        assert cls.test_id, "No test found for threat hunt creation"
        cls.crwd_threat_hunt_id = str(uuid.uuid4())
        cls.mde_threat_hunt_id = str(uuid.uuid4())
        cls.state = dict()

    def test_create_threat_hunt(self, build):
        self.state["expected_threat_hunt"] = unwrap(build.create_threat_hunt)(
            build,
            control=Control.CROWDSTRIKE,
            name="test CRWD threat hunt",
            query="#repo=base_sensor | ContextImageFileName = /prelude_dropper.exe/",
            test_id=self.test_id,
            threat_hunt_id=self.crwd_threat_hunt_id,
        )

        unwrap(build.create_threat_hunt)(
            build,
            control=Control.DEFENDER,
            name="test MDE threat hunt",
            query="DeviceProcessEvents | where isnotempty(FileName) and isnotempty(InitiatingProcessFolderPath) and isnotempty(DeviceId) | take 5",
            test_id=self.test_id,
            threat_hunt_id=self.mde_threat_hunt_id,
        )

        expected = dict(
            account_id=self.account.headers["account"],
            control=Control.CROWDSTRIKE.value,
            id=self.crwd_threat_hunt_id,
            name="test CRWD threat hunt",
            query="#repo=base_sensor | ContextImageFileName = /prelude_dropper.exe/",
            test_id=self.test_id,
        )

        diffs = check_dict_items(expected, self.state["expected_threat_hunt"])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_threat_hunt(self, detect):
        res = unwrap(detect.get_threat_hunt)(
            detect, threat_hunt_id=self.crwd_threat_hunt_id
        )

        diffs = check_dict_items(self.state["expected_threat_hunt"], res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threat_hunts(self, detect):
        res = unwrap(detect.list_threat_hunts)(detect)
        owners = set([r["account_id"] for r in res])
        assert {"prelude", self.account.headers["account"]} >= owners

        mine = [r for r in res if r["id"] == self.state["expected_threat_hunt"]["id"]]
        assert 1 == len(mine)
        diffs = check_dict_items(self.state["expected_threat_hunt"], mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_threat_hunt(self, build):
        self.state["expected_threat_hunt"] = unwrap(build.update_threat_hunt)(
            build,
            name="updated threat hunt",
            query="#repo=base_sensor | FilePath = /Prelude Security/ | groupBy([@timestamp, ParentBaseFileName, ImageFileName, aid], limit=20)| sort(@timestamp, limit=20)",
            threat_hunt_id=self.crwd_threat_hunt_id,
        )
        assert self.state["expected_threat_hunt"]["name"] == "updated threat hunt"
        assert (
            self.state["expected_threat_hunt"]["query"]
            == "#repo=base_sensor | FilePath = /Prelude Security/ | groupBy([@timestamp, ParentBaseFileName, ImageFileName, aid], limit=20)| sort(@timestamp, limit=20)"
        )
