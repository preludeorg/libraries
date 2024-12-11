import pytest
import requests
import time

from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control, ControlCategory


@pytest.mark.order(8)
@pytest.mark.usefixtures('setup_account')
class TestScmAcrossControls:
    def setup_class(self):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        self.export = ExportController(pytest.account)
        self.jobs = JobsController(pytest.account)
        self.scm = ScmController(pytest.account)

    def test_evaluation_summary(self, unwrap):
        summary = unwrap(self.scm.evaluation_summary)(self.scm)
        assert {'endpoint_summary', 'user_summary', 'inbox_summary'} == summary.keys()
        assert {'categories', 'endpoint_count'} == summary['endpoint_summary'].keys()
        if categories := summary['endpoint_summary'].get('categories'):
            assert {'category', 'controls', 'endpoint_count', 'excepted'} == categories[0].keys()
            assert {'control_failure_count', 'missing_asset_manager_count', 'missing_edr_count'} == categories[0]['excepted'].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'control_failure_count', 'endpoint_count', 'no_av_policy', 'no_edr_policy',
                        'policy_conflict_count', 'reduced_functionality_mode', 'setting_count',
                        'excepted'} == controls[0].keys()
                if excepted := controls[0]['excepted']:
                    assert {'control_failure_count', 'no_av_policy', 'no_edr_policy', 'reduced_functionality_mode', 'setting_misconfiguration_count'} == excepted.keys()

        assert {'categories', 'user_count'} == summary['user_summary'].keys()
        if categories := summary['user_summary'].get('categories'):
            assert {'category', 'controls', 'user_count', 'excepted'} == categories[0].keys()
            assert {'control_failure_count'} == categories[0]['excepted'].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'control_failure_count', 'user_count', 'setting_count', 'excepted'} == controls[0].keys()
                assert {'control_failure_count', 'setting_misconfiguration_count'} == controls[0]['excepted'].keys()

        assert {'categories', 'inbox_count'} == summary['inbox_summary'].keys()
        if categories := summary['inbox_summary'].get('categories'):
            assert {'category', 'controls', 'inbox_count'} == categories[0].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'inbox_count', 'setting_count', 'excepted'} == controls[0].keys()
                assert {'setting_misconfiguration_count'} == controls[0]['excepted'].keys()

    def test_technique_summary(self, unwrap):
        summary = unwrap(self.scm.technique_summary)(self.scm, 'T1078,T1027')
        assert len(summary) > 0
        assert {'controls', 'technique'} == summary[0].keys()
        assert len(summary[0]['controls']) > 0
        assert {'control', 'setting_count', 'setting_misconfiguration_count'} == summary[0]['controls'][0].keys()

    def test_export_missing_edr_endpoints_csv(self, unwrap):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        job_id = unwrap(self.export.export_scm)(self.export, 'endpoints/?$filter=missing_edr eq true&$top=1')['job_id']
        while (result := unwrap(self.jobs.job_status)(self.jobs, job_id))['end_time'] is None:
            time.sleep(3)
        assert result['successful']
        csv = requests.get(
                result['results']['url'],
                timeout=10
            ).content.decode('utf-8')
        assert len(csv.strip('\r\n').split('\r\n')) == 2


@pytest.mark.order(9)
@pytest.mark.usefixtures('setup_account')
@pytest.mark.parametrize('control', [c for c in Control if c.category != ControlCategory.NONE])
class TestScmPerControl:
    def setup_class(self):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        self.scm = ScmController(pytest.account)
        self.jobs = JobsController(pytest.account)

    @pytest.fixture(scope='function', autouse=True)
    def setup_and_teardown(self, control):
        if control.value not in pytest.controls:
            pytest.skip(f'{control.name} not attached')
        yield

    def test_update_evaluation(self, unwrap, control):
        try:
            job_id = unwrap(self.scm.update_evaluation)(self.scm, control)['job_id']
            while (result := unwrap(self.jobs.job_status)(self.jobs, job_id))['end_time'] is None:
                time.sleep(3)
            assert result['successful']
        except Exception as e:
            if 'job is already running' in str(e):
                pytest.skip('Skipping due to existing job initiated from partner attach')
            else:
                raise e

    def test_evaluation(self, unwrap, control):
        evaluation = unwrap(self.scm.evaluation)(self.scm, control)
        if 'endpoint_evaluation' in evaluation:
            evaluation = evaluation['endpoint_evaluation']
            assert {'policies'} == evaluation.keys()
            if control.category == ControlCategory.XDR:
                assert len(evaluation['policies']) > 0
                assert {'id', 'name', 'platform', 'settings', 'conflict_count', 'endpoint_count', 'success_count'} == evaluation['policies'][0].keys()
            else:
                assert len(evaluation['policies']) == 0
        elif 'user_evaluation' in evaluation:
            evaluation = evaluation['user_evaluation']
            assert {'policies'} == evaluation.keys()
            assert len(evaluation['policies']) > 0
            assert {'id', 'name', 'noncompliant_hostnames', 'settings', 'user_count'} == evaluation['policies'][0].keys()
        elif 'inbox_evaluation' in evaluation:
            evaluation = evaluation['inbox_evaluation']
            assert {'policies'} == evaluation.keys()
            assert len(evaluation['policies']) > 0
            assert {'id', 'name', 'settings', 'inbox_count'} == evaluation['policies'][0].keys()
        else:
            assert False, 'No evaluation returned'
