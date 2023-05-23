import os
import uuid
import pytest

from datetime import datetime
from importlib.resources import files

from tests import templates as templates
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController


@pytest.mark.order(after='test_partner_controller.py::TestPartnerController::test_detach_partner')
class TestBuildController:

    def setup_class(self):
        """Setup the test class"""
        self.test_id = str(uuid.uuid4())
        self.test_name = 'test'
        self.build = BuildController(pytest.account)
        self.detect = DetectController(pytest.account)

    def test_create_test(self, unwrap):
        """Test create_test method"""
        unwrap(self.build.create_test)(self.build, test_id=self.test_id, name=self.test_name, unit='bulletin')
        pytest.test_id = self.test_id
        assert True

    def test_upload(self, unwrap):
        """Test upload method"""
        template = files(templates).joinpath('template.go').read_text()
        template = template.replace('$ID', self.test_id)
        template = template.replace('$NAME', self.test_name)
        template = template.replace('$CREATED', str(datetime.utcnow()))
        unwrap(self.build.upload)(self.build, test_id=self.test_id, filename=f'{self.test_id}.go', data=template)
        res = unwrap(self.detect.get_test)(self.detect, test_id=self.test_id)
        assert f'{self.test_id}.go' in res['attachments']

    @pytest.mark.order(after='test_detect_controller.py::TestDetectController::test_disable_test')
    def test_delete_test(self, unwrap):
        """Test delete_test method"""
        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id)
        assert True
