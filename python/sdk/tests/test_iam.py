import json
import pytest

from prelude_sdk.controllers.iam_controller import (
    IAMAccountController,
    IAMUserController,
)
from prelude_sdk.models.codes import Permission

from testutils import *


@pytest.mark.order(1)
@pytest.mark.usefixtures("setup_account")
class TestIAM:

    def setup_class(self):
        self.iam_account = IAMAccountController(pytest.account)
        self.iam_user = IAMUserController(pytest.account)
        self.company = "prelude"
        self.service_user = "registration"

    def test_get_account(self, unwrap):
        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_accounts(self, unwrap):
        res = unwrap(self.iam_user.list_accounts)(self.iam_user)
        assert pytest.expected_account["account_id"] in [a["account_id"] for a in res]

    def test_create_service_user(self, unwrap):
        service_user = unwrap(self.iam_account.create_service_user)(
            self.iam_account, name=self.service_user
        )
        assert self.service_user == service_user["name"]
        assert check_if_string_is_uuid(service_user["token"])
        pytest.second_service_user_handle = service_user["handle"]

        res = unwrap(self.iam_account.get_account)(self.iam_account)

        for user in res["token_users"]:
            if user["handle"] != service_user["handle"]:
                continue
            pytest.expected_account["token_users"].append(
                dict(
                    created=user["created"],
                    handle=service_user["handle"],
                    last_seen=user["last_seen"],
                    name=self.service_user,
                    oidc="",
                    permission=Permission.SERVICE.value,
                )
            )

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_delete_service_user(self, unwrap):
        unwrap(self.iam_account.delete_service_user)(
            self.iam_account, handle=pytest.second_service_user_handle
        )

        for i, user in enumerate(pytest.expected_account["token_users"]):
            if user["handle"] == pytest.second_service_user_handle:
                del pytest.expected_account["token_users"][i]
                break

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_user(self, unwrap):
        unwrap(self.iam_user.update_user)(self.iam_user, name="Robb")

        for user in pytest.expected_account["users"]:
            if user["handle"] == pytest.account.handle:
                user["name"] = "Robb"
                break

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_account(self, unwrap):
        unwrap(self.iam_account.update_account)(self.iam_account, company=self.company)
        pytest.expected_account["company"] = self.company

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_audit_logs(self, unwrap):
        res = unwrap(self.iam_account.audit_logs)(self.iam_account, limit=1)[0]
        expected = dict(
            event="update_account",
            user_id=pytest.expected_account["whoami"]["handle"],
            status="200",
            values=dict(company=self.company),
            account_id=pytest.expected_account["account_id"],
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_invite_account_user(self, unwrap):
        pytest.second_user = second_email = (
            f"second-{str(uuid.uuid4())[:12]}@auto-accept.developer.preludesecurity.com"
        )
        unwrap(self.iam_account.invite_user)(
            self.iam_account,
            email=pytest.second_user,
            oidc=None,
            permission=Permission.EXECUTIVE,
            name="second",
        )
        pytest.expected_account = unwrap(self.iam_account.get_account)(self.iam_account)

    def test_update_account_user(self, unwrap):
        unwrap(self.iam_account.update_account_user)(
            self.iam_account,
            email=pytest.second_user,
            oidc="",
            permission=Permission.ADMIN,
        )

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        for user in pytest.expected_account["users"]:
            if user["handle"] == pytest.second_user:
                user["permission"] = Permission.ADMIN.value
                break

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_remove_account_user(self, unwrap):
        unwrap(self.iam_account.remove_user)(
            self.iam_account, email=pytest.second_user, oidc=""
        )

        for i, user in enumerate(pytest.expected_account["users"]):
            if user["handle"] == pytest.second_user:
                del pytest.expected_account["users"][i]
                break

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_forgot_password(self, manual, pause_for_manual_action, unwrap):
        if not manual:
            pytest.skip("Not manual mode")

        self.iam_user.forgot_password()
        with pause_for_manual_action:
            code = input("\nEnter your confirmation code:\n")
        password = "PySdkTests123!"
        self.iam_user.confirm_forgot_password(
            confirmation_code=code, new_password=password
        )
        pytest.account.password_login(password)
        pytest.account.headers["authorization"] = f"Bearer {pytest.account.token}"
        self.iam_account = IAMAccountController(pytest.account)

        res = unwrap(self.iam_account.get_account)(self.iam_account)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    @pytest.mark.order(-3)
    def test_delete_service_user(self, unwrap):
        unwrap(self.iam_account.delete_service_user)(
            self.iam_account, handle=pytest.service_user_handle
        )

    @pytest.mark.order(-2)
    def test_purge_account(self, unwrap, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        iam = IAMAccountController(pytest.account)
        unwrap(iam.purge_account)(iam)

    @pytest.mark.order(-1)
    def test_purge_user(self, unwrap, existing_account):
        if not existing_account:
            iam = IAMUserController(pytest.account)
            unwrap(iam.purge_user)(iam)
