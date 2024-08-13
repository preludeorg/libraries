import os
import pytest
import time

from prelude_sdk.controllers.generate_controller import GenerateController
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import Control

from testutils import *

@pytest.mark.order(9)
@pytest.mark.usefixtures('setup_account')
class TestGenerate:

    def setup_class(self):
        if not pytest.expected_account['features']['threat_intel']:
            pytest.skip("THREAT_INTEL feature not enabled")

        self.iam = IAMController(pytest.account)
        self.generate = GenerateController(pytest.account)

        self.threat_intel_pdf = os.path.dirname(os.path.realpath(__file__)) + '/data/threat_intel.pdf'

    def test_upload_threat_intel(self, unwrap):
        try:
            unwrap(self.iam.accept_terms)(self.iam, name='threat_intel', version='1.0.0')
        except Exception as e:
            pass

        res = unwrap(self.generate.upload_threat_intel)(self.generate, file=self.threat_intel_pdf)
        job_id = res['job_id']
        assert check_if_string_is_uuid(job_id)

        while True:
            time.sleep(5)
            res = unwrap(self.generate.get_threat_intel)(self.generate, job_id=job_id)
            match status := res.get('status'):
                case 'RUNNING':
                    if res['step'] == 'GENERATE':
                        assert 2 == res['num_tasks'], json.dumps(res)
                case 'COMPLETE':
                    assert 14 == len(res['output']), json.dumps(res)
                    for output in res['output']:
                        assert {'status', 'technique'} < set(output.keys()), json.dumps(output)
                        assert 'ai_generated' in output or 'existing_test' in output or 'excluded' in output, json.dumps(output)
                    return
                case 'FAILED':
                    assert False, f'threat_gen FAILED: {json.dumps(res)}'
                case _:
                    assert False, f' Unexpected status: {status}\n Response: {json.dumps(res)}'

    def test_generate_from_partner_advisory(self, unwrap):
        res = unwrap(self.iam.get_account)(self.iam)
        partners = [p['id'] for p in res['controls']]
        if Control.CROWDSTRIKE.value not in partners:
            pytest.skip('CROWDSTRIKE not attached')

        res = unwrap(self.generate.generate_from_partner_advisory)(self.generate, partner=Control.CROWDSTRIKE, advisory_id=pytest.crowdstrike_advisory_id)
        job_id = res['job_id']
        assert check_if_string_is_uuid(job_id)

        while True:
            time.sleep(5)
            res = unwrap(self.generate.get_threat_intel)(self.generate, job_id=job_id)
            match status := res.get('status'):
                case 'COMPLETE':
                    for output in res['output']:
                        assert {'status', 'technique'} < set(output.keys()), json.dumps(output)
                        assert 'ai_generated' in output or 'existing_test' in output or 'excluded' in output, json.dumps(output)
                    return
