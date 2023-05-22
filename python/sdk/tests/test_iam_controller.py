import time
import uuid
import pytest

from datetime import datetime, timedelta
from prelude_sdk.models.codes import Permission, Mode
from prelude_sdk.controllers.iam_controller import IAMController


class Account:
    def __init__(self, account_id='', token='', hq=''):
        self.hq = hq
        self.profile = 'test'
        self.headers = dict(
            account=account_id,
            token=token,
            _product='py-sdk'
        )

    def read_keychain_config(self):
        return {self.profile: dict()}


    def write_keychain_config(self, cfg):
        pass


def check_if_string_is_uuid(string):
    try:
        uuid.UUID(string)
        return True
    except ValueError:
        return False


class TestIAMController:

    @pytest.mark.order(1)
    def test_new_account(self, unwrap, pause_for_manual_action, email, api):
        """Test new_account method"""
        pytest.account = Account(hq=api)
        iam = IAMController(pytest.account)
        res = unwrap(iam.new_account)(iam, user_email=email, user_name='Bob')
        if email.endswith('@auto-accept.developer.preludesecurity.com'):
            time.sleep(5)
        else:
            with pause_for_manual_action:
                input("Press ENTER to continue testing after verifying the account...\n")
        pytest.account.headers['account'] = res['account_id']
        pytest.account.headers['token'] = res['token']
        assert len(pytest.account.headers['account']) == 32
        assert check_if_string_is_uuid(pytest.account.headers['token'])

    @pytest.mark.order(2)
    def test_get_account(self, unwrap, email):
        """Test get_account method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.get_account)(iam)
        assert res['whoami'] == email
        assert res['mode'] == 0

    @pytest.mark.order(3)
    def test_create_user(self, unwrap):
        """Test create_user method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.create_user)(iam, email='registration', permission=Permission.SERVICE.value, name='Rob', expires=(datetime.utcnow() + timedelta(days=1)))
        assert check_if_string_is_uuid(res['token'])
        res = unwrap(iam.get_account)(iam)
        assert len([user for user in res['users'] if user['handle'] == 'registration']) == 1

    @pytest.mark.order(4)
    def test_delete_user(self, unwrap):
        """Test delete_user method"""
        iam = IAMController(pytest.account)
        unwrap(iam.delete_user)(iam, handle='registration')
        res = unwrap(iam.get_account)(iam)
        assert len([user for user in res['users'] if user['handle'] == 'registration']) == 0

    @pytest.mark.order(after='test_detect_controller.py::TestDetectController::test_describe_activity')
    def test_update_account(self, unwrap):
        """Test update_account method"""
        iam = IAMController(pytest.account)
        unwrap(iam.update_account)(iam, mode=Mode.FROZEN.value)
        res = unwrap(iam.get_account)(iam)
        assert res['mode'] == Mode.FROZEN.value

    @pytest.mark.order(after='test_detect_controller.py::TestDetectController::test_delete_endpoint')
    def test_purge_account(self, unwrap):
        """Test purge_account method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.purge_account)(iam)
        assert res is not None
