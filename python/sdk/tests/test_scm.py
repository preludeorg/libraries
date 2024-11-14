import pytest

from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control, ControlCategory


@pytest.mark.order(8)
@pytest.mark.usefixtures('setup_account')
class TestScmAcrossControls:
    def setup_class(self):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        self.export = ExportController(pytest.account)
        self.scm = ScmController(pytest.account)

    def test_evaluation_summary(self, unwrap):
        summary = unwrap(self.scm.evaluation_summary)(self.scm)
        assert {'endpoint_summary', 'user_summary', 'inbox_summary'} == summary.keys()
        assert {'categories', 'endpoint_count'} == summary['endpoint_summary'].keys()
        if categories := summary['endpoint_summary'].get('categories'):
            assert {'category', 'controls', 'endpoint_count', 'control_failure_count'} == categories[0].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'control_failure_count', 'endpoint_count', 'policy_conflict_count', 'setting_count',
                        'setting_misconfiguration_count', 'no_av_policy', 'no_edr_policy',
                        'reduced_functionality_mode'} == controls[0].keys()

        assert {'categories', 'user_count'} == summary['user_summary'].keys()
        if categories := summary['user_summary'].get('categories'):
            assert {'category', 'controls', 'user_count', 'control_failure_count'} == categories[0].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'control_failure_count', 'user_count', 'setting_count', 'setting_misconfiguration_count'} == controls[0].keys()

        assert {'categories', 'inbox_count'} == summary['inbox_summary'].keys()
        if categories := summary['inbox_summary'].get('categories'):
            assert {'category', 'controls', 'inbox_count'} == categories[0].keys()
            if controls := categories[0].get('controls'):
                assert {'control', 'inbox_count', 'setting_count', 'setting_misconfiguration_count'} == controls[0].keys()

    def test_technique_summary(self, unwrap):
        summary = unwrap(self.scm.technique_summary)(self.scm, 'T1078,T1027')
        assert len(summary) > 0
        assert {'controls', 'technique'} == summary[0].keys()
        assert len(summary[0]['controls']) > 0
        assert {'control', 'setting_count', 'setting_misconfiguration_count'} == summary[0]['controls'][0].keys()

    def test_export_missing_edr_endpoints_csv(self, unwrap):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        csv = unwrap(self.export.export_scm)(self.export, 'endpoints/?$filter=missing_edr eq true&$top=2').decode('utf-8')
        assert len(csv.split('\n')) == 3


@pytest.mark.order(9)
@pytest.mark.usefixtures('setup_account')
@pytest.mark.parametrize('control', [c for c in Control if c.category != ControlCategory.NONE])
class TestScmPerControl:
    def setup_class(self):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        self.scm = ScmController(pytest.account)

    @pytest.fixture(scope='function', autouse=True)
    def setup_and_teardown(self, control):
        if control.value not in pytest.controls:
            pytest.skip(f'{control.name} not attached')
        yield

    def test_update_evaluation(self, unwrap, control):
        try:
            unwrap(self.scm.update_evaluation)(self.scm, control)
        except Exception as e:
            if 'job is already running' in str(e):
                pytest.skip('Skipping due to existing job initiated from partner attach')
            else:
                raise e

    def test_evaluation(self, unwrap, control):
        evaluation = unwrap(self.scm.evaluation)(self.scm, control)
        if 'endpoint_evaluation' in evaluation:
            evaluation = evaluation['endpoint_evaluation']
            assert {'policies', 'misconfigured', 'total_endpoint_count'} == evaluation.keys()
            if control.category == ControlCategory.XDR:
                assert len(evaluation['policies']) > 0
            else:
                assert len(evaluation['policies']) == 0
            assert {'no_av_policy_count', 'no_edr_policy_count', 'missing_control_count', 'reduced_functionality_mode_count'} == evaluation['misconfigured'].keys()
        elif 'user_evaluation' in evaluation:
            evaluation = evaluation['user_evaluation']
            assert {'policies', 'misconfigured', 'total_user_count'} == evaluation.keys()
            assert {'missing_mfa_count'} == evaluation['misconfigured'].keys()
            assert len(evaluation['policies']) > 0
        elif 'inbox_evaluation' in evaluation:
            evaluation = evaluation['inbox_evaluation']
            assert {'policies', 'total_inbox_count'} == evaluation.keys()
            assert len(evaluation['policies']) > 0
        else:
            assert False, 'No evaluation returned'
