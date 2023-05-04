import os
import uuid
import pytest

from datetime import datetime
from importlib.resources import files

from tests import templates as templates
from prelude_sdk.controllers.build_controller import BuildController


@pytest.mark.order(after='test_partner_controller.py::TestPartnerController::test_detach_partner')
class TestBuildController:

    def setup_class(self):
        """Setup the test class"""
        self.test_id = str(uuid.uuid4())
        self.test_name = 'test'
        self.test_unit = 'AV'
        self.build = BuildController(pytest.account)

    def test_create_test(self, unwrap):
        """Test create_test method"""
        unwrap(self.build.create_test)(self.build, test_id=self.test_id, name=self.test_name, unit=self.test_unit)
        assert True

    def test_get_test(self, unwrap):
        """Test get_test method"""
        res = unwrap(self.build.get_test)(self.build, test_id=self.test_id)
        assert res['id'] == self.test_id
        assert res['name'] == self.test_name
        assert res['unit'] == self.test_unit

    def test_upload(self, unwrap):
        """Test upload method"""
        template = files(templates).joinpath('template.go').read_text()
        template = template.replace('$ID', self.test_id)
        template = template.replace('$NAME', self.test_name)
        template = template.replace('$CREATED', str(datetime.utcnow()))
        unwrap(self.build.upload)(self.build, test_id=self.test_id, filename=f'{self.test_id}.go', data=template)
        res = unwrap(self.build.get_test)(self.build, test_id=self.test_id)
        assert f'{self.test_id}.go' in res['attachments']

    def test_download(self, unwrap):
        """Test download method"""
        res = unwrap(self.build.download)(self.build, test_id=self.test_id, filename=f'{self.test_id}.go')
        assert res is not None
        with open(f'{self.test_id}.go', 'wb') as f:
            f.write(res)
        assert os.path.isfile(f'{self.test_id}.go')
        os.remove(f'{self.test_id}.go')

    def test_delete_test(self, unwrap):
        """Test delete_test method"""
        unwrap(self.build.delete_test)(self.build, test_id=self.test_id)
        assert True
