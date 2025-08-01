import json
import logging
import os
import pytest

from prelude_sdk.models.codes import Permission
from testutils import *


@pytest.mark.stage1
@pytest.mark.order(2)
class TestIAM:

    @pytest.fixture(autouse=True, scope="class")
    def _inject_shared_fixtures(self, request):
        # This runs once per class and injects the fixture values to class-level vars
        cls = self.__class__
        logging.info(f"Starting {cls.__name__} in PID {os.getpid()}")
        cls.account, cls.expected_account = request.getfixturevalue(
            "setup_existing_account"
        )

        cls.company = "prelude"
        cls.service_user_name = "registration"
        cls.second_user_handle = (
            f"second-{str(uuid.uuid4())[:12]}@auto-accept.developer.preludesecurity.com"
        )
        cls.state = dict()

    def test_get_account(self, iam_account):
        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_accounts(self, iam_user):
        res = unwrap(iam_user.list_accounts)(iam_user)
        assert self.expected_account["account_id"] in [a["account_id"] for a in res]

    def test_create_service_user(self, iam_account):
        res = unwrap(iam_account.create_service_user)(
            iam_account, name=self.service_user_name
        )
        assert self.service_user_name == res["name"]
        assert check_if_string_is_uuid(res["token"])
        self.state["service_user_handle"] = res["handle"]

        res = unwrap(iam_account.get_account)(iam_account)

        for user in res["token_users"]:
            if user["handle"] != self.state["service_user_handle"]:
                continue
            self.expected_account["token_users"].append(
                dict(
                    created=user["created"],
                    handle=self.state["service_user_handle"],
                    last_seen=user["last_seen"],
                    name=self.service_user_name,
                    oidc="",
                    permission=Permission.SERVICE.value,
                )
            )

        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_delete_service_user(self, iam_account):
        unwrap(iam_account.delete_service_user)(
            iam_account, handle=self.state["service_user_handle"]
        )

        for i, user in enumerate(self.expected_account["token_users"]):
            if user["handle"] == self.state["service_user_handle"]:
                del self.expected_account["token_users"][i]
                break

        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_user(self, iam_account, iam_user):
        unwrap(iam_user.update_user)(iam_user, name="MAKK")

        for user in self.expected_account["users"]:
            if user["handle"] == self.account.handle:
                user["name"] = "MAKK"
                break

        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_account(self, iam_account):
        unwrap(iam_account.update_account)(iam_account, company=self.company)
        self.expected_account["company"] = self.company

        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_audit_logs(self, iam_account):
        res = unwrap(iam_account.audit_logs)(iam_account, limit=10)
        actual = [r for r in res if r["event"] == "update_account"][0]
        expected = dict(
            event="update_account",
            user_id=self.expected_account["whoami"]["handle"],
            status="200",
            values=dict(company=self.company),
            account_id=self.expected_account["account_id"],
        )
        diffs = check_dict_items(expected, actual)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_invite_account_user(self, iam_account):
        unwrap(iam_account.invite_user)(
            iam_account,
            email=self.second_user_handle,
            oidc=None,
            permission=Permission.EXECUTIVE,
            name="second",
        )
        self.expected_account = unwrap(iam_account.get_account)(iam_account)

    def test_update_account_user(self, iam_account):
        unwrap(iam_account.update_account_user)(
            iam_account,
            email=self.second_user_handle,
            oidc="",
            permission=Permission.ADMIN,
        )

        res = unwrap(iam_account.get_account)(iam_account)
        for user in self.expected_account["users"]:
            if user["handle"] == self.second_user_handle:
                user["permission"] = Permission.ADMIN.value
                break

        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_remove_account_user(self, iam_account):
        unwrap(iam_account.remove_user)(
            iam_account, email=self.second_user_handle, oidc=""
        )

        for i, user in enumerate(self.expected_account["users"]):
            if user["handle"] == self.second_user_handle:
                del self.expected_account["users"][i]
                break

        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_forgot_password(
        self, manual, pause_for_manual_action, iam_account, iam_user
    ):
        if not manual:
            pytest.skip("Not manual mode")

        iam_user.forgot_password()
        with pause_for_manual_action:
            code = input("\nEnter your confirmation code:\n")
        password = "PySdkTests123!"
        iam_user.confirm_forgot_password(confirmation_code=code, new_password=password)
        self.account.password_login(password)
        self.account.headers["authorization"] = f"Bearer {self.account.token}"

        res = unwrap(iam_account.get_account)(iam_account)
        diffs = check_dict_items(self.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)
