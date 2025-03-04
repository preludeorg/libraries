import json
import pytest

from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import Mode, Permission

from testutils import *


@pytest.mark.order(1)
@pytest.mark.usefixtures("setup_account")
class TestIAM:

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.company = "prelude"
        self.service_user = "registration"

    def test_get_account(self, unwrap):
        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_accounts(self, unwrap):
        res = unwrap(self.iam.list_accounts)(self.iam)
        assert pytest.expected_account["account_id"] in [a["account_id"] for a in res]

    def test_create_service_user(self, unwrap):
        service_user = unwrap(self.iam.create_service_user)(
            self.iam, email=self.service_user
        )
        assert self.service_user == service_user["handle"]
        assert check_if_string_is_uuid(service_user["token"])

        res = unwrap(self.iam.get_account)(self.iam)

        pytest.expected_account["token_users"].append(
            dict(
                handle=self.service_user,
                permission=Permission.SERVICE.value,
                name="",
                subscriptions=[],
                oidc="",
                terms={},
            )
        )

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_remove_user(self, unwrap):
        unwrap(self.iam.remove_user)(self.iam, email=self.service_user, oidc="")

        for i, user in enumerate(pytest.expected_account["token_users"]):
            if user["handle"] == self.service_user:
                del pytest.expected_account["token_users"][i]
                break

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_user(self, unwrap):
        unwrap(self.iam.update_user)(self.iam, name="Robb")

        for user in pytest.expected_account["users"]:
            if user["handle"] == pytest.account.handle:
                user["name"] = "Robb"
                break

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_account(self, unwrap):
        unwrap(self.iam.update_account)(self.iam, company=self.company)
        pytest.expected_account["company"] = self.company

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_audit_logs(self, unwrap):
        res = unwrap(self.iam.audit_logs)(self.iam, limit=1)[0]
        expected = dict(
            event="update_account",
            user_id=pytest.expected_account["whoami"]["handle"],
            status="200",
            values=dict(company=self.company),
            account_id=pytest.expected_account["account_id"],
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_admin_reset_password(self, unwrap, manual, pause_for_manual_action, email):
        if not manual:
            pytest.skip("Not manual mode")

        unwrap(self.iam.admin_reset_password)(self.iam, email=email)
        with pause_for_manual_action:
            password = input("Enter your changed password:\n")
        pytest.account.password_login(pytest.account.handle, password)
        res = unwrap(self.iam.get_account)(self.iam)
        assert pytest.expected_account["whoami"]["handle"] == res["whoami"]["handle"]

    def test_update_account_user(self, unwrap, manual):
        if not manual:
            pytest.skip("Not manual mode")

        unwrap(self.iam.update_account_user)(
            self.iam, email=self.invited_user, oidc="", permission=Permission.ADMIN
        )

        res = unwrap(self.iam.get_account)(self.iam)

        for user in pytest.expected_account["users"]:
            if user["handle"] == self.invited_user:
                user["permission"] = Permission.ADMIN.value
                break

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    @pytest.mark.order(-2)
    def test_purge_account(self, unwrap, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        iam = IAMController(pytest.account)
        unwrap(iam.purge_account)(iam)

    @pytest.mark.order(-1)
    def test_purge_user(self, unwrap, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        iam = IAMController(pytest.account)
        unwrap(iam.purge_user)(iam)
