import uuid
import pytest

from datetime import datetime, timedelta
from prelude_sdk.models.codes import Permission, Mode
from prelude_sdk.controllers.iam_controller import IAMController


class Account:
    def __init__(self, account_id='', token='', hq='https://api.staging.preludesecurity.com'):
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

    def setup_class(self):
        """Setup the test class"""
        self.email_handle = 'alex+testingframework@preludesecurity.com'

    @pytest.mark.order(1)
    def test_new_account(self, unwrap, pause_for_manual_action):
        """Test new_account method"""
        pytest.account = Account()
        iam = IAMController(pytest.account)
        res = unwrap(iam.new_account)(iam, handle=self.email_handle)
        with pause_for_manual_action:
            input("Press ENTER to continue testing after verifying the account...\n")
        pytest.account.headers['account'] = res['account_id']
        pytest.account.headers['token'] = res['token']
        assert check_if_string_is_uuid(pytest.account.headers['account'])
        assert check_if_string_is_uuid(pytest.account.headers['token'])

    @pytest.mark.order(2)
    def test_get_account(self, unwrap):
        """Test get_account method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.get_account)(iam)
        assert res['whoami'] == self.email_handle
        assert res['mode'] == 0

    @pytest.mark.order(3)
    def test_create_user(self, unwrap):
        """Test create_user method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.create_user)(iam, handle='registration', permission=Permission.SERVICE.value, expires=(datetime.utcnow() + timedelta(days=1)))
        assert check_if_string_is_uuid(res['token'])
        res = unwrap(iam.get_account)(iam)
        assert len([user for user in res['users'] if user['handle'] == 'registration']) == 1

    @pytest.mark.order(4)
    def test_update_account(self, unwrap):
        """Test update_account method"""
        iam = IAMController(pytest.account)
        unwrap(iam.update_account)(iam, mode=Mode.AUTOPILOT.value)
        res = unwrap(iam.get_account)(iam)
        assert res['mode'] == Mode.AUTOPILOT.value

    @pytest.mark.order(5)
    def test_attach_control(self, unwrap):
        """Test attach_control method"""
        try:
            iam = IAMController(pytest.account)
            unwrap(iam.attach_control)(iam, 'crowdstrike', 'https://api.us-2.crowdstrike.com', 'test')
        except Exception as e:
            assert 'Authentication failed with crowdstrike' in str(e)

    @pytest.mark.order(6)
    def test_detach_control(self, unwrap):
        """Test detach_control method"""
        try:
            iam = IAMController(pytest.account)
            unwrap(iam.detach_control)(iam, 'crowdstrike')
        except Exception as e:
            assert 'No control by that name' in str(e)

    @pytest.mark.order(after='test_detect_controller.py::TestDetectController::test_make_decision')
    def test_purge_account(self, unwrap):
        """Test purge_account method"""
        iam = IAMController(pytest.account)
        res = unwrap(iam.purge_account)(iam)
        assert res is not None