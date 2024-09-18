import json
import pytest

from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import AuditEvent, Mode, Permission, RunCode

from testutils import *


@pytest.mark.order(1)
@pytest.mark.usefixtures('setup_account')
class TestIAM:

    def setup_class(self):
        self.iam = IAMController(pytest.account)

        self.company = 'prelude'
        self.second_user = 'registration'
        self.subscription_event = AuditEvent.CREATE_USER

    def test_new_account(self, email, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        created = pytest.expected_account

        assert 32 == len(pytest.account.headers['account'])
        assert check_if_string_is_uuid(pytest.account.headers['token'])
        assert email == created['whoami']

        pytest.expected_account = dict(
            account_id=created['account_id'],
            whoami=email,
            slug=created['account_id'],
            company='pysdk-tests',
            mode=Mode.AUTOPILOT.value,
            controls=[],
            users=[
                dict(
                    handle=email,
                    permission=Permission.ADMIN.value,
                    name='Bob',
                    subscriptions=[],
                    oidc=False,
                    terms={},
                )
            ],
            probe_sleep='600s',
            oidc=dict(),
            features=dict(
                threat_intel=False,
                detections=False
            )
        )
        pytest.expected_account['users'][0]['expires'] = created['users'][0]['expires']
        pytest.expected_account['queue'] = created['queue']
        if created['queue']:
            assert 'autopilot' == created['queue'][0]['tag']
            assert RunCode.SMART.value == created['queue'][0]['run_code']

    def test_account_subscribe(self, unwrap):
        res = unwrap(self.iam.subscribe)(self.iam, event=self.subscription_event)

        for user in pytest.expected_account['users']:
            if user['handle'] == pytest.expected_account['whoami']:
                user['subscriptions'].append(self.subscription_event.value)
                self.expected_subs = user['subscriptions']
                break

        expected = dict(
            email=pytest.expected_account['whoami'],
            subscriptions=self.expected_subs
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_account(self, unwrap):
        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_create_user(self, unwrap):
        ex = datetime.now(timezone.utc) + timedelta(days=1)
        res = unwrap(self.iam.create_user)(self.iam, email=self.second_user, permission=Permission.SERVICE, name='Rob',
                                           expires=ex)
        assert self.second_user == res['handle']
        assert check_if_string_is_uuid(res['token'])

        res = unwrap(self.iam.get_account)(self.iam)

        pytest.expected_account['users'].append(
            dict(
                handle=self.second_user,
                permission=Permission.SERVICE.value,
                name='Rob',
                subscriptions=[],
                oidc=False,
                terms={},
                expires=ex.isoformat()
            )
        )

        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_account_unsubscribe(self, unwrap):
        res = unwrap(self.iam.unsubscribe)(self.iam, event=self.subscription_event)

        for user in pytest.expected_account['users']:
            if user['handle'] == pytest.expected_account['whoami']:
                user['subscriptions'].remove(self.subscription_event.value)
                self.expected_subs = user['subscriptions']
                break

        expected = dict(
            email=pytest.expected_account['whoami'],
            subscriptions=self.expected_subs
        )
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_user(self, unwrap):
        ex = datetime.now(timezone.utc) + timedelta(days=365)
        unwrap(self.iam.update_user)(self.iam, email=self.second_user, name='Robb', expires=ex)

        for i, user in enumerate(pytest.expected_account['users']):
            if user['handle'] == self.second_user:
                user['name'] = 'Robb'
                user['expires'] = ex.isoformat()
                break

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_accept_terms(self, unwrap):
        for user in pytest.expected_account['users']:
            if user['handle'] == pytest.expected_account['whoami']:
                if user['terms'].get('threat_intel', {}).get('1.0.0'):
                    with pytest.raises(Exception) as e:
                        unwrap(self.iam.accept_terms)(self.iam, name='threat_intel', version='1.0.0')
                    return

        unwrap(self.iam.accept_terms)(self.iam, name='threat_intel', version='1.0.0')
        res = unwrap(self.iam.get_account)(self.iam)

        for user in res['users']:
            if user['handle'] == pytest.expected_account['whoami']:
                assert user['terms'].get('threat_intel', {}).get('1.0.0'), json.dumps(user, indent=2)
                assert parse(user['terms']['threat_intel']['1.0.0']) <= datetime.now(timezone.utc)
                break

        pytest.expected_account['users'] = res['users']

    def test_delete_user(self, unwrap):
        unwrap(self.iam.delete_user)(self.iam, handle=self.second_user)

        for i, user in enumerate(pytest.expected_account['users']):
            if user['handle'] == self.second_user:
                break
        del pytest.expected_account['users'][i]

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_account(self, unwrap):
        unwrap(self.iam.update_account)(self.iam, mode=Mode.MANUAL, company=self.company)
        pytest.expected_account['mode'] = Mode.MANUAL.value
        pytest.expected_account['company'] = self.company
        autopilot = [i for i, item in enumerate(pytest.expected_account['queue']) if item['tag'] == 'autopilot']
        for i in sorted(autopilot, reverse=True):
            del pytest.expected_account['queue'][i]

        res = unwrap(self.iam.get_account)(self.iam)
        diffs = check_dict_items(pytest.expected_account, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_audit_logs(self, unwrap):
        res = unwrap(self.iam.audit_logs)(self.iam, limit=1)[0]
        expected = dict(
            event='update_account',
            user_id=pytest.expected_account['whoami'],
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
    def test_purge_account(self, unwrap, existing_account):
        if existing_account:
            pytest.skip("Pre-existing account")

        iam = IAMController(pytest.account)
        unwrap(iam.purge_account)(iam)
