import json
import time
import pytest

from dateutil.parser import parse
from datetime import datetime, timedelta
from prelude_sdk.models.codes import AuditEvent, Mode, Permission, RunCode
from prelude_sdk.controllers.iam_controller import IAMController

from testutils import *


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


@pytest.mark.order(1)
class TestIAM:

    def setup_class(self):
        self.iam = IAMController(Account())

        self.company = 'prelude'
        self.second_user = 'registration'

    def test_new_account(self, unwrap, manual, pause_for_manual_action, email, api):
        pytest.account = Account(hq=api)
        self.iam.account = pytest.account
        res = unwrap(self.iam.new_account)(self.iam, user_email=email, user_name='Bob')
        if manual:
            with pause_for_manual_action:
                input("Press ENTER to continue testing after verifying the account...\n")
        else:
            time.sleep(5)
        assert 32 == len(res['account_id'])
        assert email == res['handle']
        assert check_if_string_is_uuid(res['token'])

        pytest.account.headers['account'] = res['account_id']
        pytest.account.headers['token'] = res['token']
        print(f'[account_id: {res["account_id"]}]', end=' ')

        pytest.expected_account = dict(
            account_id=res['account_id'],
            whoami=email,
            slug=res['account_id'],
            company='',
            mode=Mode.AUTOPILOT.value,
            controls=[],
            users=[
                dict(
                    handle=email,
                    permission=Permission.ADMIN.value,
                    name='Bob',
                    subscriptions=[],
                    oidc=False
                )
            ],
            queue=[
                dict(
                    run_code=RunCode.SMART.value,
                    tag='autopilot'
                )
            ],
            probe_sleep='600s',
            oidc=dict(),
            oidc_enabled=False
        )

    def test_account_subscribe(self, unwrap, manual, email):
        if not manual:
            pytest.skip("Not manual mode")

        res = unwrap(self.iam.subscribe)(self.iam, event=AuditEvent.CREATE_USER)
        expected = dict(
            email=email,
            subscriptions=[AuditEvent.CREATE_USER.value]
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

        pytest.expected_account['users'][0]['subscriptions'] = res['subscriptions']

    def test_get_account(self, unwrap, manual):
        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)
        if manual:
            assert parse(res['users'][0]['expires']) >= datetime.utcnow() + timedelta(days=364)
        else:
            assert parse(res['users'][0]['expires']) <= datetime.utcnow() + timedelta(days=1)

    def test_create_user(self, unwrap):
        res = unwrap(self.iam.create_user)(self.iam, email=self.second_user, permission=Permission.SERVICE, name='Rob',
                                      expires=(datetime.utcnow() + timedelta(days=1)))
        assert self.second_user == res['handle']
        assert check_if_string_is_uuid(res['token'])


        res = unwrap(self.iam.get_account)(self.iam)

        pytest.second_user_index = 0 if res['users'][0]['name'] == 'Rob' else 1
        pytest.expected_account['users'].insert(pytest.second_user_index,
                                                dict(
                                                    handle=self.second_user,
                                                    permission=Permission.SERVICE.value,
                                                    name='Rob',
                                                    subscriptions=[],
                                                    oidc=False
                                                )
        )

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res['users'][1]['expires']) <= datetime.utcnow() + timedelta(days=1)

    def test_account_unsubscribe(self, unwrap, manual, email):
        if not manual:
            pytest.skip("Not manual mode")

        res = unwrap(self.iam.unsubscribe)(self.iam, event=AuditEvent.CREATE_USER)
        expected = dict(
            email=email,
            subscriptions=[]
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

        pytest.expected_account['users'][0]['subscriptions'] = res['subscriptions']

    def test_update_user(self, unwrap):
        unwrap(self.iam.update_user)(self.iam, email=self.second_user, name='Robb',
                                     expires=(datetime.utcnow() + timedelta(days=365)))
        pytest.expected_account['users'][pytest.second_user_index]['name'] = 'Robb'

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res['users'][pytest.second_user_index]['expires']) >= datetime.utcnow() + timedelta(days=360)

    def test_delete_user(self, unwrap):
        unwrap(self.iam.delete_user)(self.iam, handle=self.second_user)
        del pytest.expected_account['users'][pytest.second_user_index]

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_account(self, unwrap):
        unwrap(self.iam.update_account)(self.iam, mode=Mode.MANUAL, company=self.company)
        pytest.expected_account['mode'] = Mode.MANUAL.value
        pytest.expected_account['company'] = self.company
        pytest.expected_account['queue'] = []

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_audit_logs(self, unwrap, email):
        res = unwrap(self.iam.audit_logs)(self.iam, limit=1)[0]
        expected = dict(
            event='update_account',
            user_id=email,
            status='200',
            values=dict(mode=Mode.MANUAL.name, company=self.company),
            account_id=pytest.expected_account['account_id']
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_reset_account(self, unwrap, manual, pause_for_manual_action, email):
        if not manual:
            pytest.skip("Not manual mode")

        unwrap(self.iam.reset_password)(self.iam, email=email, account_id=pytest.expected_account['account_id'])
        with pause_for_manual_action:
            token = input("Enter your verification token:\n")
        res = unwrap(self.iam.verify_user)(self.iam, token=token)
        assert pytest.expected_account['account_id'] == res['account']
        assert check_if_string_is_uuid(res['token'])

        pytest.account.headers['token'] = res['token']

    @pytest.mark.order(-1)
    def test_purge_account(self, unwrap):
        iam = IAMController(pytest.account)
        unwrap(iam.purge_account)(iam)
