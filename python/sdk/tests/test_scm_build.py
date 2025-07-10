import pytest
from datetime import datetime, timezone, timedelta

from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control, ControlCategory


@pytest.mark.order(8)
@pytest.mark.usefixtures("setup_account")
class TestScmBuild:
    def setup_class(self):
        if not pytest.expected_account["features"]["policy_evaluator"]:
            pytest.skip("POLICY_EVALUATOR feature not enabled")
        self.scm = ScmController(pytest.account)

    def test_create_object_exception(self, unwrap):
        res = unwrap(self.scm.create_object_exception)(
            self.scm,
            ControlCategory.ASSET_MANAGER,
            "hostname eq 'host1'",
            name="filter me",
            expires="5555-05-05",
        )
        assert res["exception_id"]
        pytest.exception_id = res["exception_id"]

    def test_update_object_exception(self, unwrap):
        res = unwrap(self.scm.update_object_exception)(
            self.scm,
            pytest.exception_id,
            filter="hostname eq 'host2'",
            expires=None,
        )
        assert res["status"]

    def test_list_object_exceptions(self, unwrap):
        res = unwrap(self.scm.list_object_exceptions)(self.scm)
        exception = [x for x in res if x["id"] == pytest.exception_id]
        assert len(exception) == 1
        exception = exception[0]
        del exception["author"]
        del exception["created"]
        assert exception == {
            "category": ControlCategory.ASSET_MANAGER.value,
            "expires": None,
            "filter": "hostname eq 'host2'",
            "id": pytest.exception_id,
            "name": "filter me",
        }

    def test_delete_object_exception(self, unwrap):
        res = unwrap(self.scm.delete_object_exception)(self.scm, pytest.exception_id)
        assert res["status"]
        res = unwrap(self.scm.list_object_exceptions)(self.scm)
        assert not any(x["id"] == pytest.exception_id for x in res)
