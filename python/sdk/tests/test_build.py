import json
import os
import pytest
import time
import uuid
from datetime import datetime, timedelta
from importlib.resources import files

from dateutil.parser import parse

from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController

import templates
from testutils import *


@pytest.mark.order(2)
class TestBuild:

    def setup_class(self):
        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

        self.test_id = str(uuid.uuid4())
        self.name = 'test'
        self.updated_name = 'updated_test'
        self.unit = 'custom'
        self.technique = 'T1234.001'

    def test_create_test(self, unwrap):
        res = unwrap(self.build.create_test)(self.build, test_id=self.test_id, name=self.name, unit=self.unit)

        pytest.test_id = self.test_id
        pytest.expected_test = dict(
            account_id=pytest.account.headers['account'],
            id=self.test_id,
            name=self.name,
            unit=self.unit,
            technique=None,
            attachments=[],
            tombstoned=None
        )

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_upload(self, unwrap):
        template = files(templates).joinpath('template.go').read_text()
        res = unwrap(self.build.upload)(self.build, test_id=self.test_id, filename=f'{self.test_id}.go',
                                        data=template.encode("utf-8"))

        expected = dict(
            id=self.test_id,
            filename=f'{self.test_id}.go'
        )
        assert expected == res

        pytest.expected_test['attachments'].append(res['filename'])

    def test_get_test(self, unwrap):
        def wait_for_compile():
            timeout = time.time() + 60
            while time.time() < timeout:
                time.sleep(6)
                res = unwrap(self.detect.get_test)(self.detect, test_id=self.test_id)
                if len(res['attachments']) == 6:
                    break
                # Hack to clear test from cache
                unwrap(self.build.update_test)(self.build, test_id=self.test_id, name=self.name)
            return

        wait_for_compile()
        for suffix in ['darwin-arm64', 'darwin-x86_64', 'linux-arm64', 'linux-x86_64', 'windows-x86_64']:
            pytest.expected_test['attachments'].append(f'{self.test_id}_{suffix}')
        res = unwrap(self.detect.get_test)(self.detect, test_id=self.test_id)

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_tests(self, unwrap):
        res = unwrap(self.detect.list_tests)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert owners == {'prelude', pytest.account.headers['account']}

        mine = [r for r in res if r['account_id'] == pytest.account.headers['account']]
        assert 1 == len(mine)
        del pytest.expected_test['attachments']
        diffs = check_dict_items(pytest.expected_test, mine[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_update_test(self, unwrap):
        res = unwrap(self.build.update_test)(self.build, test_id=self.test_id, name=self.updated_name, technique=self.technique)

        pytest.expected_test['name'] = self.updated_name
        pytest.expected_test['technique'] = self.technique

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_download(self, unwrap):
        filename = f'{self.test_id}.go'
        res = unwrap(self.detect.download)(self.detect, test_id=self.test_id, filename=filename)
        assert res is not None
        with open(filename, 'wb') as f:
            f.write(res)
        assert os.path.isfile(filename)
        os.remove(filename)

    @pytest.mark.order(-2)
    def test_delete_test(self, unwrap):
        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id, purge=False)
        res = unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)
        pytest.expected_test['tombstoned'] = res['tombstoned']

        diffs = check_dict_items(pytest.expected_test, res)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(res['tombstoned']) <= datetime.utcnow() + timedelta(minutes=1)

        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id, purge=True)
        with pytest.raises(Exception):
            unwrap(self.detect.get_test)(self.detect, test_id=pytest.test_id)


@pytest.mark.order(3)
class TestThreat:

    def setup_class(self):
        self.detect = DetectController(pytest.account)

        self.threat_id = '09d1a6b6-64d0-4473-af02-9a72b386cc79'

    def test_get_threat(self, unwrap):
        res = unwrap(self.detect.get_threat)(self.detect, threat_id=self.threat_id)

        pytest.threat_id = self.threat_id
        pytest.expected_threat = dict(
            account_id='prelude',
            id=self.threat_id,
            source_id='aa23-061a',
            name='#StopRansomware: Royal Ransomware',
            source='https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a',
            published='2023-11-13',
            tests=['881f9052-fb52-4daf-9ad2-0a7ad9615baf', 'b74ad239-2ddd-4b1e-b608-8397a43c7c54'],
            tombstoned=None
        )

        diffs = check_dict_items(pytest.expected_threat, res)
        assert not diffs, json.dumps(diffs, indent=2)

    def test_list_threats(self, unwrap):
        res = unwrap(self.detect.list_threats)(self.detect)
        owners = set([r['account_id'] for r in res])
        assert owners == {'prelude'}

        threat = [r for r in res if r['id'] == pytest.threat_id][0]
        diffs = check_dict_items(pytest.expected_threat, threat)
        assert not diffs, json.dumps(diffs, indent=2)
