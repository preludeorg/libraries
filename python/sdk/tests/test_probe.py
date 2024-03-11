import json
import os
import pytest
import subprocess
from datetime import datetime, timedelta

from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.probe_controller import ProbeController
from prelude_sdk.models.codes import RunCode


@pytest.mark.order(7)
class TestProbe:

    def setup_class(self):
        self.iam = IAMController(pytest.account)
        self.detect = DetectController(pytest.account)
        self.probe = ProbeController(pytest.account)

        self.host = 'olive'
        self.serial = 'abc-123'

    def test_create_endpoint(self, unwrap):
        pytest.token = unwrap(self.detect.register_endpoint)(self.detect, host=self.host, serial_num=self.serial)

        res = unwrap(self.detect.list_endpoints)(self.detect)
        ep = [r for r in res if r['serial_num'] == self.serial]
        pytest.endpoint_id = ep[0]['endpoint_id']

    def test_schedule(self, unwrap):
        unwrap(self.detect.schedule)(
            self.detect,
            [
                dict(test_id='9f410a6b-76b6-45d6-b80f-d7365add057e', run_code=RunCode.DEBUG.name, tags=''),
                dict(test_id='b74ad239-2ddd-4b1e-b608-8397a43c7c54', run_code=RunCode.RUN_ONCE.name, tags=''),
                # 2 tests in this threat (881.., b74...)
                dict(threat_id=pytest.threat_id, run_code=RunCode.DAILY.name, tags=''),
                # windows only test
                dict(test_id='f12d00db-571f-4c51-a536-12a3577b5a4b', run_code=RunCode.DEBUG.name, tags=''),
                # should not run
                dict(test_id='8f9558f3-d451-46e3-bdda-97378c1e8ce4', run_code=RunCode.DAILY.name, tags='diff-tag')
            ]
        )

        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 5 == len(queue), json.dumps(queue, indent=2)

    def test_download_probe(self):
        probe_name = 'nocturnal'
        res = self.probe.download(name=probe_name, dos='darwin-arm64')
        assert res is not None

        with open(f'{probe_name}.sh', 'w') as f:
            f.write(res)
        assert os.path.isfile(f'{probe_name}.sh')
        pytest.probe_file = os.path.abspath(f'{probe_name}.sh')
        os.chmod(pytest.probe_file, 0o755)

    def test_describe_activity(self, unwrap):
        try:
            with pytest.raises(subprocess.TimeoutExpired):
                subprocess.run([pytest.probe_file], capture_output=True, env={'PRELUDE_TOKEN': pytest.token}, timeout=40)

            filters = dict(
                start=datetime.utcnow() - timedelta(days=7),
                finish=datetime.utcnow() + timedelta(days=1),
                endpoints=pytest.endpoint_id
            )
            res = unwrap(self.detect.describe_activity)(self.detect, view='logs', filters=filters)
            assert 5 == len(res), json.dumps(res, indent=2)
        finally:
            os.remove(pytest.probe_file)

    def test_unschedule(self, unwrap):
        unwrap(self.detect.unschedule)(
            self.detect,
            [
                dict(test_id='9f410a6b-76b6-45d6-b80f-d7365add057e', tags=''),
                dict(test_id='b74ad239-2ddd-4b1e-b608-8397a43c7c54', tags=''),
                dict(threat_id=pytest.threat_id, tags=''),
                dict(test_id='f12d00db-571f-4c51-a536-12a3577b5a4b', tags=''),
                dict(test_id='8f9558f3-d451-46e3-bdda-97378c1e8ce4', tags='diff-tag')
            ]
        )

        queue = unwrap(self.iam.get_account)(self.iam)['queue']
        assert 0 == len(queue), json.dumps(queue, indent=2)

    def test_delete_endpoint(self, unwrap):
        unwrap(self.detect.delete_endpoint)(self.detect, ident=pytest.endpoint_id)
        res = unwrap(self.detect.list_endpoints)(self.detect)
        assert 0 == len(res), json.dumps(res, indent=2)
