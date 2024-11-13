import pytest

from prelude_sdk.models.codes import Control
from prelude_sdk.controllers.scm_controller import ScmController


def pytest_generate_tests(metafunc):
    if metafunc.cls is TestPolicyEvaluation:
        idlist = [x[0] for x in metafunc.cls.controls]
        metafunc.parametrize(['control', 'is_edr'], [[Control[x[0]], x[1]] for x in metafunc.cls.controls], ids=idlist, scope='class')


@pytest.mark.order(9)
@pytest.mark.usefixtures('setup_account')
class TestPolicyEvaluationSummary:

    def setup_class(self):
        self.scm = ScmController(pytest.account)

    def test_get_policy_evaluation_summary(self, unwrap):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
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

@pytest.mark.order(10)
@pytest.mark.usefixtures('setup_account')
class TestPolicyEvaluation:
    controls = [
        ('crowdstrike', True),
        ('defender', True),
        ('sentinelone', True),
        ('intune', False),
    ]

    def setup_class(self):
        self.scm = ScmController(pytest.account)

    def test_update_policy_evaluation(self, unwrap, control, is_edr):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        try:
            unwrap(self.scm.update_evaluation)(self.scm, control)
        except Exception as e:
            if 'job is already running' in str(e):
                pytest.skip('Skipping due to existing job initiated from partner attach')
            else:
                raise e

    def test_get_policy_evaluation(self, unwrap, control, is_edr):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        evaluation = unwrap(self.scm.evaluation)(self.scm, control)
        if 'endpoint_evaluation' in evaluation:
            evaluation = evaluation['endpoint_evaluation']
            assert {'policies', 'misconfigured', 'total_endpoint_count'} == evaluation.keys()
            if is_edr:
                assert len(evaluation['policies']) > 0
            else:
                assert len(evaluation['policies']) == 0
            assert {'no_av_policy_count', 'no_edr_policy_count', 'missing_control_count', 'reduced_functionality_mode_count'} == evaluation['misconfigured'].keys()
        if 'user_evaluation' in evaluation:
            evaluation = evaluation['user_evaluation']
            assert {'policies', 'misconfigured', 'total_user_count'} == evaluation.keys()
            assert {'missing_mfa_count'} == evaluation['misconfigured'].keys()
        if 'inbox_evaluation' in evaluation:
            evaluation = evaluation['inbox_evaluation']
            assert {'policies, total_inbox_count'} == evaluation.keys()
