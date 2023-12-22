import os
import pytest

from prelude_sdk.controllers.partner_controller import PartnerController
from prelude_sdk.models.codes import Control


@pytest.mark.order(after='test_iam_controller.py::TestIAMController::test_new_account')
class TestPartnerController:

    def setup_class(self):
        """Setup the test class"""
        self.partner = PartnerController(pytest.account)
        self.control = Control.CROWDSTRIKE
        self.api = 'https://api.preludesecurity.com'
        self.user = 'test'
        self.secret = 'test'
        self.test_id = 'not-a-uuid'

    def test_attach_failed(self, unwrap):
        """Test attach method failed"""
        res = None
        try:
            res = unwrap(self.partner.attach)(self.partner, partner=self.control, api=self.api, user=self.user, secret=self.secret)
        except Exception as e:
            assert f'Failed to connect to partner' in str(e)
        
        assert False if res is not None else True, f'{str(res)} should fail with invalid credentials'

    def test_detach_failed(self, unwrap):
        """Test detach method failed"""
        res = None
        try:
            res = unwrap(self.partner.detach)(self.partner, partner=self.control)
        except Exception as e:
            assert f'Partner not found' in str(e)

        assert False if res is not None else True, f'{str(res)} should fail with partner not attached'
    
    def test_block_failed(self, unwrap):
        """Test block method failed"""
        res = None
        try:
            res = unwrap(self.partner.block)(self.partner, partner=self.control, test_id=self.test_id)
        except Exception as e:
            assert f'Partner {self.control.name} is not attached to this account' in str(e)

        assert False if res is not None else True, f'{str(res)} should fail with partner is not attached' 