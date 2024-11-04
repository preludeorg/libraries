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
        export_url = unwrap(self.export.partner)(self.export, 'endpoints/?$filter=missing_edr eq true')
        assert 'url' in export_url
