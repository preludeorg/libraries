import os
import pytest
import requests

from datetime import datetime, timedelta
from prelude_sdk.models.codes import Control
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.partner_controller import PartnerController

from testutils import *


crowdstrike = ("crowdstrike",
               dict(
                   # endpoint
                   host='Mahinas-MacBook-Pro.local',
                   edr_id='0b4bedce421e4338a7cb2f7c40b99a9b',
                   control=Control.CROWDSTRIKE,
                   os='Ventura (13)',
                   platform='darwin',
                   policy='731180f1d7294302a8934c972d71392a',
                   policy_name='Phase 3 - optimal protection',
                   # partner
                   partner_api=os.getenv('CROWDSTRIKE_API'),
                   user=os.getenv('CROWDSTRIKE_USER'),
                   secret=os.getenv('CROWDSTRIKE_SECRET'),
                   webhook_keys={'url', 'description', 'secret'}
               ))

defender = ("defender",
            dict(
                # endpoint
                host='desktop-vs2aj6k',
                edr_id='17e491f75f40da854a7171666c0d2974926fa92f',
                control=Control.DEFENDER,
                os='Windows11',
                platform='windows',
                policy=None,
                policy_name=None,
                # partner
                partner_api=os.getenv('DEFENDER_API'),
                user=os.getenv('DEFENDER_USER'),
                secret=os.getenv('DEFENDER_SECRET'),
                webhook_keys={'url', 'description', 'secret', 'headers'}
            ))

sentinel_one = ("sentinel_one",
                dict(
                    # endpoint
                    host='ip-172-31-91-156.ec2.internal',
                    edr_id='1885110387239488349',
                    control=Control.SENTINELONE,
                    os='Linux (Amazon 2023 6.1.75-99.163.amzn2023.x86_64)',
                    platform='linux',
                    policy='account/1723291585224869190/site/1723291586072118613/group/1723291586088895830',
                    policy_name='Prelude Security / Default site / Default Group',
                    # partner
                    partner_api=os.getenv('S1_API'),
                    user=os.getenv('S1_USER'),
                    secret=os.getenv('S1_SECRET'),
                    webhook_keys={'url', 'description', 'secret', 'headers'}
                ))


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    if metafunc.cls is TestPartner:
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            if not all([scenario[1][k] for k in ['partner_api', 'user', 'secret']]):
                argvalues.append(pytest.param(*[x[1] for x in items], marks=pytest.mark.skip('Creds not supplied')))
            else:
                argvalues.append([x[1] for x in items])
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


@pytest.mark.order(4)
class TestPartner:
    scenarios = [crowdstrike, defender, sentinel_one]

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.detect = DetectController(pytest.account)
        self.partner = PartnerController(pytest.account)

        self.host = 'pardner-host'

    def test_attach(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Create first endpoint (before attaching partner)
        pytest.token = unwrap(self.detect.register_endpoint)(self.detect, host=host, serial_num=host)
        pytest.endpoint_1 = dict(host=host, serial_num=host, edr_id=edr_id, control=control.value, tags=[], dos=None,
                               os=os, policy=policy, policy_name=policy_name)

        # Attach partner
        res = unwrap(self.partner.attach)(self.partner, partner=control, api=partner_api, user=user, secret=secret)
        expected = dict(api=partner_api, connected=True)
        assert expected == res

        # Create second endpoint (after partner is attached)
        unwrap(self.detect.register_endpoint)(self.detect, host=host, serial_num=host + '2')
        pytest.endpoint_2 = pytest.endpoint_1 | dict(serial_num=host + '2')

    def test_get_account(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Check partner is attached to account
        res = unwrap(self.iam.get_account)(self.iam)
        expected = [dict(api=partner_api, id=control.value)]
        assert expected == res['controls']

    def test_list_endpoints(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        try:
            # List endpoints
            res = unwrap(self.detect.list_endpoints)(self.detect)
            assert len(res) >= 2
            sorted_res = {r['serial_num']: r for r in res}
            pytest.endpoint_1['endpoint_id'] = sorted_res[pytest.endpoint_1['serial_num']]['endpoint_id']
            pytest.endpoint_2['endpoint_id'] = sorted_res[pytest.endpoint_2['serial_num']]['endpoint_id']
            expected = {e['serial_num']: e for e in [pytest.endpoint_1, pytest.endpoint_2]}
            diffs = check_dict_items(expected, sorted_res)
            assert not diffs, json.dumps(diffs, indent=2)
        finally:
            # Delete second endpoint
            unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_2['endpoint_id'])

    def test_partner_endpoints(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Show Crowdstrike endpoints
        res = unwrap(self.partner.endpoints)(self.partner, partner=control, platform=platform, hostname=host)
        expected = {edr_id: {'hostname': host, 'os': os}}
        if policy:
            expected[edr_id]['policy'] = policy
            expected[edr_id]['policy_name'] = policy_name
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_activity_logs(self, unwrap, api, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Save a test result
        res = requests.get(api, headers=dict(token=pytest.token, dos=f'{platform}-x86_64', dat=f'{pytest.test_id}:100',
                                             version='2.1'))
        assert res.status_code in [200, 302]
        pytest.endpoint_1['dos'] = f'{platform}-x86_64'

        # Check activity logs
        filters = dict(
            start=datetime.utcnow() - timedelta(days=7),
            finish=datetime.utcnow() + timedelta(days=1),
            endpoints=pytest.endpoint_1['endpoint_id']
        )
        res = unwrap(self.detect.describe_activity)(self.detect, view='logs', filters=filters)
        assert len(res) == 1, json.dumps(res, indent=2)
        expected = dict(
            test=pytest.test_id,
            endpoint_id=pytest.endpoint_1['endpoint_id'],
            status=100,
            dos=pytest.endpoint_1['dos'],
            control=control.value,
            os=os,
            policy=policy
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_generate_webhook(self, unwrap, api, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Generate webhook
        res = unwrap(self.partner.generate_webhook)(self.partner, partner=control)
        assert webhook_keys == res.keys()
        assert res['url'].startswith(f'{api}/partner/suppress/{control.name.lower()}')

    def test_block(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        # Create an IOC for the test
        res = unwrap(self.partner.block)(self.partner, partner=control, test_id=pytest.test_id)
        assert len(res) == 5
        assert {'file', 'ioc_id'} == res[0].keys()
        assert res[0]['file'].startswith(pytest.test_id)

    def test_detach(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys):
        try:
            # Detach Crowdstrike
            unwrap(self.partner.detach)(self.partner, partner=control)
            res = unwrap(self.iam.get_account)(self.iam)
            assert res['controls'] == []
        finally:
            # Delete endpoint
            unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_1['endpoint_id'])


@pytest.mark.order(5)
class TestSiems:

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.detect = DetectController(pytest.account)
        self.partner = PartnerController(pytest.account)

        self.host = 'koa'
        self.serial = '123-123-123'
        self.splunk = all([os.getenv('SPLUNK_API'), os.getenv('SPLUNK_SECRET')])
        self.vectr = all([os.getenv('VECTR_API'), os.getenv('VECTR_USER'), os.getenv('VECTR_SECRET')])
        self.s3 = bool(os.getenv('S3_BUCKET'))

        pytest.token = ''
        pytest.endpoint_id = ''
        pytest.expected_siems = []

    def test_create_endpoint(self, unwrap):
        pytest.token = unwrap(self.detect.register_endpoint)(self.detect, host=self.host, serial_num=self.serial)

        res = unwrap(self.detect.list_endpoints)(self.detect)
        ep = [r for r in res if r['serial_num'] == self.serial]
        pytest.endpoint_id = ep[0]['endpoint_id']

    def test_attach_splunk(self, unwrap):
        if not self.splunk:
            pytest.skip("Creds not supplied")

        api = os.getenv('SPLUNK_API')
        res = unwrap(self.partner.attach)(self.partner, partner=Control.SPLUNK, api=api, user='',
                                          secret=os.getenv('SPLUNK_SECRET'))
        expected = dict(api=api, connected=True)
        assert expected == res

        pytest.expected_siems.append(dict(api=api, id=Control.SPLUNK.value))

    def test_attach_vectr(self, unwrap):
        if not self.vectr:
            pytest.skip("Creds not supplied")

        api = os.getenv('VECTR_API')
        res = unwrap(self.partner.attach)(self.partner, partner=Control.VECTR, api=api, user=os.getenv('VECTR_USER'),
                                          secret=os.getenv('VECTR_SECRET'))
        expected = dict(api=api, connected=True)
        assert expected == res

        pytest.expected_siems.append(dict(api=api, id=Control.VECTR.value))

    def test_attach_s3(self, unwrap):
        if not self.s3:
            pytest.skip("Creds not supplied")

        bucket = os.getenv('S3_BUCKET')
        res = unwrap(self.partner.attach)(self.partner, partner=Control.S3, api=bucket, user='', secret='')
        expected = dict(api=bucket, connected=True)
        assert expected == res

        pytest.expected_siems.append(dict(api=bucket, id=Control.S3.value))

    def test_get_account(self, unwrap):
        res = unwrap(self.iam.get_account)(self.iam)
        assert pytest.expected_siems == res['controls']

    def test_save_result(self, unwrap, api):
        try:
            res = requests.get(api, headers=dict(token=pytest.token, dos=f'linux-x86_64', dat=f'{pytest.test_id}:101',
                                                 version='2.1'))
            assert res.status_code in [200, 302]
        finally:
            # Delete endpoint
            unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_id)

    def test_detach_splunk(self, unwrap):
        if not self.splunk:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.SPLUNK)
        res = unwrap(self.iam.get_account)(self.iam)
        del pytest.expected_siems[0]
        assert pytest.expected_siems == res['controls']

    def test_detach_vectr(self, unwrap):
        if not self.vectr:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.VECTR)
        res = unwrap(self.iam.get_account)(self.iam)
        del pytest.expected_siems[0]
        assert pytest.expected_siems == res['controls']

    def test_detach_s3(self, unwrap):
        if not self.s3:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.S3)
        res = unwrap(self.iam.get_account)(self.iam)
        del pytest.expected_siems[0]
        assert pytest.expected_siems == res['controls']
