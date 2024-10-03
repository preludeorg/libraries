import json
import os
import pytest
import time
from datetime import datetime, timedelta, timezone
from importlib.resources import files

from dateutil.parser import parse

from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import Control, EDRResponse

import templates
from testutils import *


@pytest.mark.order(2)
@pytest.mark.usefixtures('setup_account', 'setup_test')
class TestVST:

    def setup_class(self):
        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_test(self):
        expected = dict(
            account_id=pytest.account.headers['account'],
            attachments=[],
            author=pytest.expected_account['whoami'],
            expected=dict(crowdstrike=1),
            id=pytest.test_id,
            intel_context=None,
            name='test_name',
            supported_platforms=[],
            technique=None,
            tombstoned=None,
            unit='custom',
        )

        diffs = check_dict_items(expected, pytest.expected_test)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_upload(self, unwrap):
        def wait_for_compile(job_id):
            timeout = time.time() + 120
            while time.time() < timeout:
                time.sleep(5)
                res = unwrap(self.build.get_compile_status)(self.build, job_id=job_id)
                if res['status'] != 'RUNNING':
                    break
            return res

        template = files(templates).joinpath('template.go').read_text()
        res = unwrap(self.build.upload)(self.build, test_id=pytest.test_id, filename=f'{pytest.test_id}.go',
                                        data=template.encode("utf-8"))
        pytest.expected_test['attachments'].append(res['filename'])
        for suffix in ['darwin-arm64', 'darwin-x86_64', 'linux-arm64', 'linux-x86_64', 'windows-x86_64']:
            pytest.expected_test['attachments'].append(f'{pytest.test_id}_{suffix}')
        pytest.expected_test['supported_platforms'] = ['darwin', 'linux', 'windows']

        expected = dict(
            compile_job_id=res['compile_job_id'],
            filename=f'{pytest.test_id}.go',
            id=pytest.test_id,
        )
        assert expected == res

        assert res.get('compile_job_id') is not None
        res = wait_for_compile(res['compile_job_id'])
        per_platform_res = res['results']
        assert 'COMPLETE' == res['status']
        assert 5 == len(per_platform_res)
        for platform in per_platform_res:
            assert 'SUCCEEDED' == platform['status']

    def test_compile_code_string(self, unwrap):
        def wait_for_compile(job_id):
            timeout = time.time() + 60
            while time.time() < timeout:
                time.sleep(5)
                res = unwrap(self.build.get_compile_status)(self.build, job_id=job_id)
                if res['status'] != 'RUNNING':
                    break
            return res

        res = unwrap(self.build.compile_code_string)(self.build, code='package main\n\nfunc main() {}')
        assert res['job_id'] is not None
        res = wait_for_compile(res['job_id'])
        assert 'COMPLETE' == res['status']
        assert 5 == len(res['results'])
        for platform in res['results']:
            assert 'SUCCEEDED' == platform['status']

    def test_get_test(self, unwrap):
        res = unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_tests(self, unwrap):
        res = unwrap(self.detect.list_tests)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert {'prelude', pytest.account.headers['account']} >= owners

        mine = [r for r in res if r['id'] == pytest.expected_test['id']]
        assert 1 == len(mine)
        del pytest.expected_test['attachments']
        diffs = check_dict_items(pytest.expected_test | dict(detection_platforms=[]), mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_test(self, unwrap):
        updated_name = 'updated_test'
        res = unwrap(self.build.update_test)(
            self.build, crowdstrike_expected_outcome=EDRResponse.PREVENT, name=updated_name, technique='T1234.001', test_id=pytest.test_id)

        pytest.expected_test['expected']['crowdstrike'] = EDRResponse.PREVENT.value
        pytest.expected_test['name'] = updated_name
        pytest.expected_test['technique'] = 'T1234.001'

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_download(self, unwrap):
        filename = f'{pytest.test_id}.go'
        res = unwrap(self.detect.download)(self.detect, test_id=pytest.test_id, filename=filename)
        assert res is not None
        with open(filename, 'wb') as f:
            f.write(res)
        assert os.path.isfile(filename)
        os.remove(filename)

    def test_tombstone_test(self, unwrap):
        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id, purge=False)
        res = unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)
        pytest.expected_test['tombstoned'] = res['tombstoned']

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res['tombstoned']).replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) + timedelta(minutes=1)

    def test_undelete_test(self, unwrap):
        unwrap(self.build.undelete_test)(self.build, test_id=pytest.test_id)
        res = unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)
        pytest.expected_test['tombstoned'] = None

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    @pytest.mark.order(-2)
    def test_purge_test(self, unwrap):
        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id, purge=True)
        with pytest.raises(Exception):
            unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)


@pytest.mark.order(3)
@pytest.mark.usefixtures('setup_account', 'setup_test', 'setup_threat')
class TestThreat:

    def setup_class(self):
        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_threat(self):
        expected = dict(
            account_id=pytest.account.headers['account'],
            author=pytest.expected_account['whoami'],
            id=pytest.threat_id,
            name='threat_name',
            published='2023-11-13',
            source='https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a',
            source_id='aa23-061a',
            tests=['881f9052-fb52-4daf-9ad2-0a7ad9615baf', 'b74ad239-2ddd-4b1e-b608-8397a43c7c54', pytest.test_id],
            tombstoned=None
        )

        diffs = check_dict_items(expected, pytest.expected_threat)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_threat(self, unwrap):
        res = unwrap(self.detect.get_threat)(self.detect, threat_id=pytest.threat_id)

        diffs = check_dict_items(pytest.expected_threat, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threats(self, unwrap):
        res = unwrap(self.detect.list_threats)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert {'prelude', pytest.account.headers['account']} >= owners

        mine = [r for r in res if r['id'] == pytest.expected_threat['id']]
        assert 1 == len(mine)
        diffs = check_dict_items(pytest.expected_threat, mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_threat(self, unwrap):
        updated_name = 'updated-threat'
        updated_tests = ['881f9052-fb52-4daf-9ad2-0a7ad9615baf', '74077d3b-6a2f-49fa-903e-99cad6f34cf6', 'b74ad239-2ddd-4b1e-b608-8397a43c7c54']
        res = unwrap(self.build.update_threat)(self.build, threat_id=pytest.threat_id, name=updated_name, source='',
                                               tests=','.join(updated_tests))

        pytest.expected_threat['name'] = updated_name
        pytest.expected_threat['source'] = None
        pytest.expected_threat['tests'] = updated_tests

        diffs = check_dict_items(pytest.expected_threat, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_tombstone_threat(self, unwrap):
        unwrap(self.build.delete_threat)(self.build, threat_id=pytest.threat_id, purge=False)
        res = unwrap(self.detect.get_threat)(self.detect, threat_id=pytest.threat_id)
        pytest.expected_threat['tombstoned'] = res['tombstoned']

        diffs = check_dict_items(pytest.expected_threat, res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res['tombstoned']).replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) + timedelta(minutes=1)

    def test_undelete_threat(self, unwrap):
        unwrap(self.build.undelete_threat)(self.build, threat_id=pytest.threat_id)
        res = unwrap(self.detect.get_threat)(self.detect, threat_id=pytest.threat_id)
        pytest.expected_threat['tombstoned'] = None

        diffs = check_dict_items(pytest.expected_threat, res)
        assert not diffs, json.dumps

    @pytest.mark.order(-3)
    def test_purge_threat(self, unwrap):
        unwrap(self.build.delete_threat)(self.build, threat_id=pytest.threat_id, purge=True)
        with pytest.raises(Exception):
            unwrap(self.detect.get_threat)(self.detect, threat_id=pytest.threat_id)


@pytest.mark.order(4)
@pytest.mark.usefixtures('setup_account', 'setup_test', 'setup_detection')
class TestDetection:

    def setup_class(self):
        if not pytest.expected_account['features']['detections']:
            pytest.skip("DETECTIONS feature not enabled")

        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_detection(self, unwrap):
        expected = dict(
            account_id=pytest.account.headers['account'],
            id=pytest.detection_id,
            name='Suspicious Command Line Usage in Windows',
            rule=dict(
                title='Suspicious Command Line Usage in Windows',
                description='Detects suspicious use of cmd.exe or powershell.exe with commands often used for reconnaissance like directory listing, tree viewing, or searching for sensitive files.',
                logsource=dict(category='process_creation', product='windows'),
                detection=dict(condition='selection', selection=dict(ParentImage='cmd.exe')),
                level='medium'
            ),
            rule_id=pytest.expected_detection['rule_id'],
            test=pytest.test_id
        )

        diffs = check_dict_items(expected, pytest.expected_detection)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_detection(self, unwrap):
        res = unwrap(self.detect.get_detection)(self.detect, detection_id=pytest.detection_id)

        diffs = check_dict_items(pytest.expected_detection, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_detections(self, unwrap):
        res = unwrap(self.detect.list_detections)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert {'prelude', pytest.account.headers['account']} >= owners

        mine = [r for r in res if r['id'] == pytest.expected_detection['id']]
        assert 1 == len(mine)
        diffs = check_dict_items(pytest.expected_detection, mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_detection(self, unwrap):
        updated_rule = pytest.detection_rule.replace(pytest.expected_detection['rule']['title'], 'Suspicious no more')
        res = unwrap(self.build.update_detection)(self.build, detection_id=pytest.detection_id, rule=updated_rule)
        pytest.expected_detection['rule']['title'] = 'Suspicious no more'

        diffs = check_dict_items(pytest.expected_detection, res)
        assert not diffs, json.dumps(diffs, indent=2)

    @pytest.mark.order(-4)
    def test_delete_detection(self, unwrap):
        unwrap(self.build.delete_detection)(self.build, detection_id=pytest.detection_id)
        with pytest.raises(Exception):
            unwrap(self.detect.get_detection)(self.detect, detection_id=pytest.detection_id)

@pytest.mark.order(4)
@pytest.mark.usefixtures('setup_account', 'setup_test', 'setup_threat_hunt')
class TestThreatHunt:

    def setup_class(self):
        if not pytest.expected_account['features']['threat_intel']:
            pytest.skip("threat intel feature not enabled")

        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_threat_hunt(self, unwrap):
        expected = dict(
            account_id=pytest.account.headers['account'],
            control=Control.CROWDSTRIKE.value,
            id=pytest.crwd_threat_hunt_id,
            name='test CRWD threat hunt',
            query='#repo=base_sensor | ImageFileName is not null | ParentBaseFileName is not null',
            test_id=pytest.test_id,
        )

        diffs = check_dict_items(expected, pytest.expected_threat_hunt)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_get_threat_hunt(self, unwrap):
        res = unwrap(self.detect.get_threat_hunt)(self.detect, threat_hunt_id=pytest.crwd_threat_hunt_id)

        diffs = check_dict_items(pytest.expected_threat_hunt, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threat_hunts(self, unwrap):
        res = unwrap(self.detect.list_threat_hunts)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert {'prelude', pytest.account.headers['account']} >= owners

        mine = [r for r in res if r['id'] == pytest.expected_threat_hunt['id']]
        assert 1 == len(mine)
        diffs = check_dict_items(pytest.expected_threat_hunt, mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_threat_hunt(self, unwrap):
        pytest.expected_threat_hunt = unwrap(self.build.update_threat_hunt)(
            self.build,
            name='updated threat hunt',
            query='#repo=base_sensor | ImageFileName is not null | ParentBaseFileName is not null | aid is not null',
            threat_hunt_id=pytest.crwd_threat_hunt_id)
        assert pytest.expected_threat_hunt['name'] == 'updated threat hunt'
        assert pytest.expected_threat_hunt['query'] == '#repo=base_sensor | ImageFileName is not null | ParentBaseFileName is not null | aid is not null'

    @pytest.mark.order(-4)
    def test_delete_threat_hunt(self, unwrap):
        unwrap(self.build.delete_threat_hunt)(self.build, threat_hunt_id=pytest.crwd_threat_hunt_id)
        with pytest.raises(Exception):
            unwrap(self.detect.get_threat_hunt)(self.detect, threat_hunt_id=pytest.crwd_threat_hunt_id)
