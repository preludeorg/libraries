import pytest

from prelude_sdk.controllers.export_controller import ExportController


@pytest.mark.order(12)
@pytest.mark.usefixtures('setup_account')
class TestPartner:

    def setup_class(self):
        self.export = ExportController(pytest.account)

    def test_export_missing_control_csv(self, unwrap):
        export_url = unwrap(self.export.partner)(self.export, 'missing_control')
        assert 'url' in export_url
