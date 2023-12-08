import os
import time
import uuid
import pytest

from datetime import datetime
from importlib.resources import files

from tests import templates as templates
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController


class TestBuildController:

    def setup_class(self):
        """Setup the test class"""
        self.test_id = str(uuid.uuid4())
        self.test_name = 'test'
        self.test_updated_name = 'updated_test'
        self.test_unit = 'AV'
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
        template = template.replace('$UNIT', self.test_unit)
        template = template.replace('$CREATED', str(datetime.utcnow()))
        unwrap(self.build.upload)(self.build, test_id=self.test_id, filename=f'{self.test_id}.go', data=template.encode("utf-8"))
        time.sleep(5)
        res = unwrap(self.detect.get_test)(self.detect, test_id=self.test_id)
        assert f'{self.test_id}.go' in res['attachments']

    def test_update_test(self, unwrap):
        """Test update_test method"""
        res = unwrap(self.build.update_test)(self.build, test_id=self.test_id, name=self.test_updated_name)
        assert res['name'] == self.test_updated_name

    @pytest.mark.order(after='test_detect_controller.py::TestDetectController::test_disable_test')
    def test_delete_test(self, unwrap):
        """Test delete_test method"""
        unwrap(self.build.delete_test)(self.build, test_id=pytest.test_id)
        assert True
