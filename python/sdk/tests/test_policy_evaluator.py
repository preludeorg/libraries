import pytest

from prelude_sdk.models.codes import Control
from prelude_sdk.controllers.partner_controller import PartnerController


def pytest_generate_tests(metafunc):
    if metafunc.cls is TestPolicyEvaluation:
        idlist = [x[0] for x in metafunc.cls.controls]
        metafunc.parametrize(['control', 'is_edr'], [[Control[x[0]], x[1]] for x in metafunc.cls.controls], ids=idlist, scope='class')


@pytest.mark.order(9)
@pytest.mark.usefixtures('setup_account')
class TestPolicyEvaluationSummary:

    def setup_class(self):
        self.partner = PartnerController(pytest.account)

    def test_get_policy_evaluation_summary(self, unwrap):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        summary = unwrap(self.partner.get_policy_evaluation_summary)(self.partner)
        assert {'endpoint_summary', 'user_summary', 'inbox_summary'} == summary.keys()
        assert {'controls', 'missing_edr_count', 'total_endpoint_count'} == summary['endpoint_summary'].keys()
        for control_summary in summary['endpoint_summary']['controls']:
            assert {'control', 'endpoint_count', 'policy_conflict_count', 'setting_misconfiguration_count'} == control_summary.keys()
        assert {'controls', 'total_user_count'} == summary['user_summary'].keys()
        for control_summary in summary['user_summary']['controls']:
            assert {'control', 'user_count', 'setting_misconfiguration_count'} == control_summary.keys()
        assert {'controls', 'total_inbox_count'} == summary['inbox_summary'].keys()
        for control_summary in summary['inbox_summary']['controls']:
            assert {'control', 'inbox_control', 'setting_misconfiguration_count'} == control_summary.keys()

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
        self.partner = PartnerController(pytest.account)

    def test_update_policy_evaluation(self, unwrap, control, is_edr):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        try:
            unwrap(self.partner.update_policy_evaluation)(self.partner, control)
        except Exception as e:
            if 'job is already running' in str(e):
                pytest.skip('Skipping due to existing job initiated from partner attach')
            else:
                raise e

    def test_get_policy_evaluation(self, unwrap, control, is_edr):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        evaluation = unwrap(self.partner.get_policy_evaluation)(self.partner, control)
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
