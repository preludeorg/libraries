import json
import pytest
import requests
from datetime import datetime, timedelta

from dateutil.parser import parse
from testutils import *

from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import RunCode


@pytest.mark.order(4)
class TestDetect:

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.detect = DetectController(pytest.account)

        self.host = 'test_host'
        self.serial = 'test_serial'
        self.tags = 'alpha'
        self.updated_tags = 'beta'

    def test_register_endpoint(self, unwrap):
        res = unwrap(self.detect.register_endpoint)(self.detect, host=self.host, serial_num=self.serial, tags=self.tags)
        assert 32 == len(res)

        pytest.token = res
        pytest.expected_endpoint = dict(
            endpoint_id='',
            host=self.host,
            serial_num=self.serial,
            edr_id=None,
            control=0,
            tags=[self.tags],
            dos=None,
            os=None,
            policy=None,
            policy_name=None
        )

    def test_list_endpoints(self, unwrap):
        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert len(res) == 1
        ep = res[0]
        pytest.expected_endpoint['endpoint_id'] = ep['endpoint_id']
        pytest.endpoint_id = ep['endpoint_id']

        diffs = check_dict_items(pytest.expected_endpoint, ep)
        assert not diffs, json.dumps(diffs, indent=2)
        assert parse(ep['last_seen']).date() == parse(ep['created']).date()

    def test_update_endpoint(self, unwrap):
        res = unwrap(self.detect.update_endpoint)(self.detect, endpoint_id=pytest.endpoint_id, tags=self.updated_tags)
        assert res['id'] == pytest.endpoint_id
        pytest.expected_endpoint['tags'] = [self.updated_tags]

        res = unwrap(self.detect.list_endpoints)(self.detect)
        diffs = check_dict_items(pytest.expected_endpoint, res[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_schedule_threat(self, unwrap):
        res = unwrap(self.detect.schedule)(self.detect, [dict(threat_id=pytest.threat_id, run_code=RunCode.DAILY.name)])
        assert 1 == len(res), json.dumps(res, indent=2)
        diffs = check_dict_items(dict(threat=pytest.threat_id, run_code=RunCode.DAILY.value, tag=None), res[0])
        assert not diffs, json.dumps(diffs, indent=2)

        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 1 == len(queue), json.dumps(queue, indent=2)
        expected = dict(
            threat=pytest.threat_id,
            run_code=RunCode.DAILY.value
        )
        diffs = check_dict_items(expected, queue[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_unschedule_threat(self, unwrap):
        unwrap(self.detect.unschedule)(self.detect, [dict(threat_id=pytest.threat_id)])
        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 0 == len(queue), json.dumps(queue, indent=2)

    def test_schedule_test(self, unwrap):
        res = unwrap(self.detect.schedule)(self.detect, [dict(test_id=pytest.test_id, run_code=RunCode.DEBUG.name, tags=self.updated_tags)])
        assert 1 == len(res), json.dumps(res, indent=2)
        diffs = check_dict_items(dict(test=pytest.test_id, run_code=RunCode.DEBUG.value, tag=self.updated_tags), res[0])
        assert not diffs, json.dumps(diffs, indent=2)

        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 1 == len(queue), json.dumps(queue, indent=2)
        expected = dict(
            test=pytest.test_id,
            run_code=RunCode.DEBUG.value,
            tag=self.updated_tags
        )
        diffs = check_dict_items(expected, queue[0])
        assert not diffs, json.dumps(diffs, indent=2)

    def test_unschedule_test(self, unwrap):
        unwrap(self.detect.unschedule)(self.detect, [dict(test_id=pytest.test_id, tags=self.updated_tags)])
        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 0 == len(queue), json.dumps(queue, indent=2)

    def test_describe_activity(self, unwrap, api):
        res = requests.get(api, headers=dict(token=pytest.token, dos=f'darwin-x86_64', dat=f'{pytest.test_id}:100',
                                             version='2.1'))
        assert res.status_code in [200, 302]
        filters = dict(
            start=datetime.utcnow() - timedelta(days=7),
            finish=datetime.utcnow() + timedelta(days=1),
            endpoints=pytest.endpoint_id
        )
        res = unwrap(self.detect.describe_activity)(self.detect, view='logs', filters=filters)
        assert 1 == len(res), json.dumps(res, indent=2)

    def test_delete_endpoint(self, unwrap):
        unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_id)
        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert 0 == len(res), json.dumps(res, indent=2)

