import json
import pytest

from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import Control

from testutils import *


@pytest.mark.order(5)
@pytest.mark.usefixtures("setup_account", "setup_test", "setup_threat_hunt")
class TestThreatHunt:

    def setup_class(self):
        if not pytest.expected_account["features"]["threat_intel"]:
            pytest.skip("threat intel feature not enabled")

        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_threat_hunt(self):
        expected = dict(
            account_id=pytest.account.headers["account"],
            control=Control.CROWDSTRIKE.value,
            id=pytest.crwd_threat_hunt_id,
            name="test CRWD threat hunt",
            query="#repo=base_sensor | ContextImageFileName = /prelude_dropper.exe/",
            test_id=pytest.test_id,
        )

        diffs = check_dict_items(expected, pytest.expected_threat_hunt)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_threat_hunt(self):
        res = unwrap(self.detect.get_threat_hunt)(
            self.detect, threat_hunt_id=pytest.crwd_threat_hunt_id
        )

        diffs = check_dict_items(pytest.expected_threat_hunt, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threat_hunts(self):
        res = unwrap(self.detect.list_threat_hunts)(self.detect)
        owners = set([r["account_id"] for r in res])
        assert {"prelude", pytest.account.headers["account"]} >= owners

        mine = [r for r in res if r["id"] == pytest.expected_threat_hunt["id"]]
        assert 1 == len(mine)
        diffs = check_dict_items(pytest.expected_threat_hunt, mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_threat_hunt(self):
        pytest.expected_threat_hunt = unwrap(self.build.update_threat_hunt)(
            self.build,
            name="updated threat hunt",
            query="#repo=base_sensor | FilePath = /Prelude Security/ | groupBy([@timestamp, ParentBaseFileName, ImageFileName, aid], limit=20)| sort(@timestamp, limit=20)",
            threat_hunt_id=pytest.crwd_threat_hunt_id,
        )
        assert pytest.expected_threat_hunt["name"] == "updated threat hunt"
        assert (
            pytest.expected_threat_hunt["query"]
            == "#repo=base_sensor | FilePath = /Prelude Security/ | groupBy([@timestamp, ParentBaseFileName, ImageFileName, aid], limit=20)| sort(@timestamp, limit=20)"
        )

    @pytest.mark.order(-7)
    def test_delete_threat_hunt(self):
        unwrap(self.build.delete_threat_hunt)(
            self.build, threat_hunt_id=pytest.crwd_threat_hunt_id
        )
        with pytest.raises(Exception):
            unwrap(self.detect.get_threat_hunt)(
                self.detect, threat_hunt_id=pytest.crwd_threat_hunt_id
            )
