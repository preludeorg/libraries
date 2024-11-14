import pytest

from prelude_sdk.controllers.export_controller import ExportController


@pytest.mark.order(13)
@pytest.mark.usefixtures('setup_account')
class TestExport:

    def setup_class(self):
        self.export = ExportController(pytest.account)

    def test_export_missing_edr_endpoints_csv(self, unwrap):
        if not pytest.expected_account['features']['policy_evaluator']:
            pytest.skip('POLICY_EVALUATOR feature not enabled')
        csv = unwrap(self.export.export_scm)(self.export, 'endpoints/?$filter=missing_edr eq true').decode('utf-8')
        assert len(csv.split('\n')) == 3
