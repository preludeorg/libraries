import os
import json
import pytest
import requests

from datetime import datetime, timedelta, timezone
from prelude_sdk.models.codes import Control
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.partner_controller import PartnerController

from testutils import *


crowdstrike = ("crowdstrike",
               dict(
                   host=os.getenv('CROWDSTRIKE_HOST'),
                   edr_id=os.getenv('CROWDSTRIKE_EDR_ID'),
                   control=Control.CROWDSTRIKE,
                   os=os.getenv('CROWDSTRIKE_OS'),
                   platform=os.getenv('CROWDSTRIKE_PLATFORM'),
                   policy=os.getenv('CROWDSTRIKE_POLICY'),
                   policy_name=os.getenv('CROWDSTRIKE_POLICY_NAME'),
                   partner_api=os.getenv('CROWDSTRIKE_API'),
                   user=os.getenv('CROWDSTRIKE_USER'),
                   secret=os.getenv('CROWDSTRIKE_SECRET'),
                   webhook_keys={'url', 'description', 'secret'},
                   group_id=os.getenv('CROWDSTRIKE_WINDOWS_IOA_GROUP_ID')
               ))

defender = ("defender",
            dict(
                host=os.getenv('DEFENDER_HOST'),
                edr_id=os.getenv('DEFENDER_EDR_ID'),
                control=Control.DEFENDER,
                os=os.getenv('DEFENDER_OS'),
                platform=os.getenv('DEFENDER_PLATFORM'),
                policy=None,
                policy_name=None,
                partner_api=os.getenv('DEFENDER_API'),
                user=os.getenv('DEFENDER_USER'),
                secret=os.getenv('DEFENDER_SECRET'),
                webhook_keys={'url', 'description', 'secret', 'headers'},
                group_id=None
            ))

sentinel_one = ("sentinel_one",
                dict(
                    host=os.getenv('S1_HOST'),
                    edr_id=os.getenv('S1_EDR_ID'),
                    control=Control.SENTINELONE,
                    os=os.getenv('S1_OS'),
                    platform=os.getenv('S1_PLATFORM'),
                    policy=os.getenv('S1_POLICY'),
                    policy_name=os.getenv('S1_POLICY_NAME'),
                    partner_api=os.getenv('S1_API'),
                    user=os.getenv('S1_USER'),
                    secret=os.getenv('S1_SECRET'),
                    webhook_keys={'url', 'description', 'secret', 'headers'},
                    group_id=None
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


@pytest.mark.order(6)
@pytest.mark.usefixtures('setup_account', 'setup_test', 'setup_detection', 'setup_threat_hunt')
class TestPartner:
    scenarios = [crowdstrike, defender, sentinel_one]

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.detect = DetectController(pytest.account)
        self.partner = PartnerController(pytest.account)

        self.host = 'pardner-host'

    def test_attach(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        # Create endpoint before attach
        pytest.token = unwrap(self.detect.register_endpoint)(self.detect, host=host, serial_num=host)
        pytest.endpoint_1 = dict(host=host, serial_num=host, edr_id=edr_id, control=control.value, tags=[], dos=None,
                                 os=os, policy=policy, policy_name=policy_name)

        # Attach partner
        res = unwrap(self.partner.attach)(self.partner, partner=control, api=partner_api, user=user, secret=secret)
        expected = dict(api=partner_api, connected=True)
        assert expected == res

        # Create endpoint after attach
        unwrap(self.detect.register_endpoint)(self.detect, host=host, serial_num=host + '2')
        pytest.endpoint_2 = pytest.endpoint_1 | dict(serial_num=host + '2')

    def test_get_account(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        res = unwrap(self.iam.get_account)(self.iam)
        expected = dict(api=partner_api, id=control.value)
        assert expected in res['controls']

    def test_list_endpoints(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        try:
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

    def test_partner_endpoints(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        res = unwrap(self.partner.endpoints)(self.partner, partner=control, platform=platform, hostname=host)
        expected = {edr_id: {'hostname': host, 'os': os}}
        if policy:
            expected[edr_id]['policy'] = policy
            expected[edr_id]['policy_name'] = policy_name
        diffs = check_dict_items(expected, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_activity_logs(self, unwrap, api, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        res = requests.get(api, headers=dict(token=pytest.token, dos=f'{platform}-x86_64', dat=f'{pytest.test_id}:100', version='2.7'))
        assert res.status_code in [200, 302]
        pytest.endpoint_1['dos'] = f'{platform}-x86_64'

        filters = dict(
            start=datetime.now(timezone.utc) - timedelta(days=1),
            finish=datetime.now(timezone.utc) + timedelta(days=1),
            endpoints=pytest.endpoint_1['endpoint_id'],
            tests=pytest.test_id,
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

    def test_generate_webhook(self, unwrap, api, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        res = unwrap(self.partner.generate_webhook)(self.partner, partner=control)
        assert webhook_keys == res.keys()
        assert res['url'].startswith(f'{api}/partner/suppress/{control.name.lower()}')

    def test_do_threat_hunt(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control == Control.SENTINELONE:
            pytest.skip('Threat hunts not supported for SENTINELONE')
        if not pytest.expected_account['features']['threat_intel']:
            pytest.skip('THREAT_INTEL feature not enabled')

        threat_hunt_id = pytest.crwd_threat_hunt_id if control == Control.CROWDSTRIKE else pytest.mde_threat_hunt_id
        res = unwrap(self.detect.do_threat_hunt)(self.detect, threat_hunt_id=threat_hunt_id)
        assert {'account_id', 'non_prelude_origin', 'prelude_origin', 'threat_hunt_id'} == set(res.keys())
        assert res['account_id'] == pytest.expected_account['account_id']
        assert res['threat_hunt_id'] == threat_hunt_id
        pytest.non_prelude_origin = res['non_prelude_origin']
        pytest.prelude_origin = res['prelude_origin']

    def test_threat_hunt_activity(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control == Control.SENTINELONE:
            pytest.skip('Threat hunts not supported for SENTINELONE')
        if not pytest.expected_account['features']['threat_intel']:
            pytest.skip('THREAT_INTEL feature not enabled')

        threat_hunt_id = pytest.crwd_threat_hunt_id if control == Control.CROWDSTRIKE else pytest.mde_threat_hunt_id
        res = unwrap(self.detect.threat_hunt_activity)(self.detect, threat_hunt_id=threat_hunt_id)
        expected = dict(
            non_prelude_origin=pytest.non_prelude_origin,
            prelude_origin=pytest.prelude_origin,
            test_id=pytest.test_id,
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_block(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control == Control.SENTINELONE:
            res = unwrap(self.partner.block)(self.partner, partner=control, test_id=pytest.test_id)
            assert 5 == len(res)
            assert {'file', 'ioc_id'} == res[0].keys()
            assert res[0]['file'].startswith(pytest.test_id)
            return
        
        if not pytest.expected_account['features']['detections']:
            pytest.skip('DETECTIONS feature not enabled')
        res = unwrap(self.partner.block)(self.partner, partner=control, test_id=pytest.test_id)
        assert res[0]['group_id'] == group_id
        assert res[0]['platform'] == pytest.expected_detection['rule']['logsource']['product']

        first_rule = res[0]['rules'][0]
        expected_name_suffix = '(0)' if control == Control.CROWDSTRIKE else '- windows'
        assert first_rule['name'] == f'{pytest.expected_test["name"]} ({pytest.detection_id[:8]}) {expected_name_suffix}'
        assert first_rule['status'] == 'CREATED', json.dumps(first_rule, indent=2)
        assert first_rule.get('ioa_id') if control == Control.CROWDSTRIKE else first_rule.get('custom_detection_id')

    def test_reports(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control != Control.CROWDSTRIKE:
            pytest.skip('IOA reports only supported for CROWDSTRIKE')
        if not pytest.expected_account['features']['detections']:
            pytest.skip('DETECTIONS feature not enabled')

        res = unwrap(self.partner.list_reports)(self.partner, partner=control, test_id=pytest.test_id)
        assert 1 == len(res)
        expected = dict(
            blocked=0,
            detected=0,
            detection_id=pytest.detection_id,
            group_id=group_id,
            monitored=0,
            platform=pytest.expected_detection['rule']['logsource']['product'],
            test_id=pytest.test_id
        )
        diffs = check_dict_items(expected, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_observed_detected(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control == Control.SENTINELONE:
            pytest.skip('Observed detected not supported for SENTINELONE')
        if not pytest.expected_account['features']['observed_detected']:
            pytest.skip('OBSERVED_DETECTED feature not enabled')

        res = unwrap(self.partner.observed_detected)(self.partner)

        assert control.name in res
        assert 1 <= len(res[control.name])
        assert {'account_id', 'detected', 'endpoint_ids', 'observed', 'test_id'} == set(res[control.name][0].keys())
        assert res[control.name][0]['account_id'] == pytest.expected_account['account_id']

    def test_ioa_stats(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        try:
            if control != Control.CROWDSTRIKE:
                pytest.skip('IOA stats only supported for CROWDSTRIKE')
            if not pytest.expected_account['features']['observed_detected']:
                pytest.skip('OBSERVED_DETECTED feature not enabled')

            res = unwrap(self.partner.ioa_stats)(self.partner)
            assert 0 == len(res)
        finally:
            unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_1['endpoint_id'])

    def test_list_advisories(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        if control != Control.CROWDSTRIKE:
            pytest.skip('List advisories only supported for CROWDSTRIKE')
        if not pytest.expected_account['features']['threat_intel']:
            pytest.skip('THREAT_INTEL feature not enabled')

        res = unwrap(self.partner.list_advisories)(self.partner, partner=control, limit=5, offset=0)
        assert 1 <= len(res['advisories'])
        assert res['advisories'][0]['id']
        assert {'created', 'description', 'id', 'name', 'tags', 'slug'} == set(res['advisories'][0].keys())
        assert res['pagination']['limit'] == 5
        assert res['pagination']['offset'] == 0
        assert res['pagination']['total'] > 0
        pytest.crowdstrike_advisory_id = res['advisories'][0]['id']

    @pytest.mark.order(-5)
    def test_detach(self, unwrap, host, edr_id, control, os, platform, policy, policy_name, partner_api, user, secret, webhook_keys, group_id):
        unwrap(self.partner.detach)(self.partner, partner=control)
        res = unwrap(self.iam.get_account)(self.iam)
        for c in res['controls']:
            assert c['id'] != control.value


@pytest.mark.order(7)
@pytest.mark.usefixtures('setup_account')
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
        for c in pytest.expected_siems:
            assert c in res['controls']

    def test_save_result(self, unwrap, api):
        try:
            res = requests.get(api, headers=dict(token=pytest.token, dos=f'linux-x86_64', dat='b74ad239-2ddd-4b1e-b608-8397a43c7c54:101', version='2.7'))
            assert res.status_code in [200, 302]
        finally:
            unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_id)

    def test_detach_splunk(self, unwrap):
        if not self.splunk:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.SPLUNK)
        res = unwrap(self.iam.get_account)(self.iam)
        for c in res['controls']:
            assert c['id'] != Control.SPLUNK.value

    def test_detach_vectr(self, unwrap):
        if not self.vectr:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.VECTR)
        res = unwrap(self.iam.get_account)(self.iam)
        for c in res['controls']:
            assert c['id'] != Control.VECTR.value

    def test_detach_s3(self, unwrap):
        if not self.s3:
            pytest.skip("Creds not supplied")

        unwrap(self.partner.detach)(self.partner, partner=Control.S3)
        res = unwrap(self.iam.get_account)(self.iam)
        for c in res['controls']:
            assert c['id'] != Control.S3.value
